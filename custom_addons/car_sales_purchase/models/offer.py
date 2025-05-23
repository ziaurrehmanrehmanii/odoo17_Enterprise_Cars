# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class CarOffer(models.Model):
    _name = 'car.offer'
    _description = 'Car Offer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'
    
    @api.model
    def _init_params(self):
        """Initialize parameters required by dependencies"""
        try:
            # Ensure CRM PLS fields parameter exists
            pls_fields = self.env['ir.config_parameter'].sudo().get_param('crm.pls_fields')
            if not pls_fields:
                self.env['ir.config_parameter'].sudo().set_param('crm.pls_fields', 'phone_state,email_state,source_id,tag_ids')
                _logger.info("Initialized crm.pls_fields parameter")
        except Exception as e:
            _logger.warning("Failed to initialize parameters: %s", str(e))
    
    name = fields.Char('Reference', readonly=True, copy=False, default='New')
    car_id = fields.Many2one('car.details', string='Car', required=True, ondelete='cascade')
    transaction_type = fields.Selection(related='car_id.transaction_type', string='Transaction Type', store=True)
    connection_id = fields.Many2one(related='car_id.connection_id', string='Connection', store=True)
    
    date = fields.Datetime('Offer Date', default=fields.Datetime.now, required=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    employee_id = fields.Many2one('hr.employee', string='PEAS Employee', domain=[('is_peas_employee', '=', True)],
                                help="Select the PEAS employee handling this offer")
    
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    price = fields.Monetary(string='Offer Price', currency_field='currency_id', required=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', tracking=True)
    
    notes = fields.Text('Notes')
    invoice_id = fields.Many2one('account.move', string='Invoice', copy=False, readonly=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        # Initialize required parameters
        self._init_params()
        
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('car.offer') or 'New'
        return super(CarOffer, self).create(vals_list)
    
    def action_send(self):
        self.write({'state': 'sent'})
    
    def action_reject(self):
        self.write({'state': 'rejected'})
    
    def action_accept(self):
        self.ensure_one()
        
        if self.state == 'accepted':
            raise UserError(_('This offer is already accepted.'))
        
        # Auto-reject all other offers for this car
        other_offers = self.env['car.offer'].search([
            ('car_id', '=', self.car_id.id),
            ('id', '!=', self.id),
            ('state', 'in', ['draft', 'sent'])
        ])
        
        if other_offers:
            other_offers.write({
                'state': 'rejected'
            })
            # Log a note about automatic rejection
            for offer in other_offers:
                offer.message_post(
                    body=_("This offer was automatically rejected because another offer was accepted."),
                    subtype_id=self.env.ref('mail.mt_note').id
                )
        
        # Update car final price and state
        self.car_id.write({
            'final_price': self.price,
            'state': 'offer_accepted'
        })
        
        # Check if we need to use special PEAS accounting
        peas_employee = self.employee_id
        use_special_accounting = (peas_employee and peas_employee.is_peas_employee and 
                                 peas_employee.journal_id and 
                                 peas_employee.receivable_account_id and 
                                 peas_employee.asset_account_id)
        
        if use_special_accounting:
            # Create a direct journal entry between receivable and asset accounts
            invoice = self._create_peas_journal_entry()
        else:
            # Use standard invoice creation
            invoice_vals = self._prepare_invoice_vals()
            invoice = self.env['account.move'].create(invoice_vals)
            # Post the invoice
            invoice.action_post()
            
        # Log PEAS employee information if applicable
        if self.employee_id and self.employee_id.is_peas_employee:
            message = _(
                "Offer accepted using PEAS employee: %s. Invoice created with journal: %s",
                self.employee_id.name,
                invoice.journal_id.name
            )
            self.message_post(body=message, subtype_id=self.env.ref('mail.mt_note').id)
            self.car_id.message_post(body=message, subtype_id=self.env.ref('mail.mt_note').id)
        
        # Link invoice to the car
        self.car_id.write({
            'invoice_id': invoice.id,
            'state': 'invoiced'
        })
        
        # Update offer state and link invoice to offer
        self.write({
            'state': 'accepted',
            'invoice_id': invoice.id
        })
        
        return {
            'name': _('Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
        }
    
    def action_view_invoice(self):
        """Open the invoice associated with this offer"""
        self.ensure_one()
        if not self.invoice_id:
            raise UserError(_('No invoice found for this offer.'))
        
        return {
            'name': _('Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'target': 'current',
        }

    def _prepare_invoice_vals(self):
        self.ensure_one()
        
        # Get partner from connection
        partner = self.connection_id
        if not partner:
            raise UserError(_('No connection defined for this car.'))
        
        # Check if a PEAS employee is assigned to this offer
        peas_employee = self.employee_id
        
        # Determine move type based on transaction type
        if self.transaction_type == 'sell':
            move_type = 'out_invoice'  # Customer Invoice
        else:  # buy
            move_type = 'in_invoice'  # Vendor Bill
        
        # Find appropriate journal and accounts
        if peas_employee and peas_employee.is_peas_employee and peas_employee.journal_id:
            # Use PEAS employee's journal
            _logger.info("Using PEAS employee's journal for this transaction: %s", peas_employee.name)
            journal = peas_employee.journal_id
            
            # Use appropriate partner based on transaction type
            if self.transaction_type == 'sell' and peas_employee.customer_id:
                partner = peas_employee.customer_id
                _logger.info("Using PEAS employee's customer account: %s", partner.name)
            elif self.transaction_type == 'buy' and peas_employee.vendor_id:
                partner = peas_employee.vendor_id
                _logger.info("Using PEAS employee's vendor account: %s", partner.name)
            
            # Get the appropriate accounts from PEAS employee
            receivable_account_id = peas_employee.receivable_account_id and peas_employee.receivable_account_id.id
            asset_account_id = peas_employee.asset_account_id and peas_employee.asset_account_id.id
            
            if not (receivable_account_id and asset_account_id):
                # Fallback to default accounts if PEAS accounts not found
                _logger.warning("PEAS employee %s is missing receivable or asset account, using default", peas_employee.name)
                account_id = self.env['account.account'].search([
                    ('account_type', '=', 'income' if self.transaction_type == 'sell' else 'expense'),
                    ('company_id', '=', self.company_id.id)
                ], limit=1).id
            else:
                # Both accounts exist - we'll use them in the invoice lines rather than the header
                account_id = asset_account_id if self.transaction_type == 'sell' else receivable_account_id
                
        else:
            # Fallback to standard journal selection if no PEAS employee or PEAS journal not found
            journal = self.env['account.journal'].search([
                ('type', '=', 'sale' if self.transaction_type == 'sell' else 'purchase'),
                ('company_id', '=', self.company_id.id)
            ], limit=1)
            
            if not journal:
                raise UserError(_('No journal found for %s transactions.') % self.transaction_type)
                
            # Use default accounts
            account_id = self.env['account.account'].search([
                ('account_type', '=', 'income' if self.transaction_type == 'sell' else 'expense'),
                ('company_id', '=', self.company_id.id)
            ], limit=1).id
        
        invoice_vals = {
            'partner_id': partner.id,
            'move_type': move_type,
            'journal_id': journal.id,
            'invoice_date': fields.Date.today(),
            'narration': f"Reference: {self.name}\n{self.notes or ''}",
        }
        
        # Create invoice line using appropriate accounts
        invoice_line_vals = {
            'name': f"{self.car_id.make} {self.car_id.model} ({self.car_id.year}) - {self.car_id.vin or ''}",
            'quantity': 1.0,
            'price_unit': self.price,
            'account_id': account_id,
        }
        
        # For PEAS employees with both accounts, we need to customize the accounting
        if peas_employee and peas_employee.is_peas_employee and peas_employee.receivable_account_id and peas_employee.asset_account_id:
            _logger.info("Creating special journal entry for PEAS employee %s using receivable and asset accounts", peas_employee.name)
        
        invoice_vals['invoice_line_ids'] = [(0, 0, invoice_line_vals)]
        
        # Add reference to the PEAS employee if applicable
        if peas_employee:
            invoice_vals['narration'] += f"\nPEAS Employee: {peas_employee.name}"
        
        return invoice_vals

    def _create_peas_journal_entry(self):
        """
        Create a direct journal entry for PEAS employee transactions
        that transfers money between receivable and asset accounts
        """
        self.ensure_one()
        peas_employee = self.employee_id
        
        if not peas_employee or not peas_employee.is_peas_employee:
            return self._prepare_invoice_vals()
            
        # Get required accounts and journal from PEAS employee
        journal = peas_employee.journal_id
        receivable_account = peas_employee.receivable_account_id
        asset_account = peas_employee.asset_account_id
        
        if not journal or not receivable_account or not asset_account:
            _logger.warning("Missing PEAS configuration - falling back to standard invoice")
            invoice_vals = self._prepare_invoice_vals()
            return self.env['account.move'].create(invoice_vals)
        
        # Get partner from connection
        partner = self.connection_id
        if not partner:
            raise UserError(_('No connection defined for this car.'))
        
        # Get the appropriate PEAS partner
        if self.transaction_type == 'sell' and peas_employee.customer_id:
            partner = peas_employee.customer_id
        elif self.transaction_type == 'buy' and peas_employee.vendor_id:
            partner = peas_employee.vendor_id
        
        # For buy: Debit asset account, Credit receivable account
        # For sell: Debit receivable account, Credit asset account
        if self.transaction_type == 'buy':
            # We're buying a car: money moves from receivable to asset
            debit_account = asset_account
            credit_account = receivable_account
        else:
            # We're selling a car: money moves from asset to receivable
            debit_account = receivable_account
            credit_account = asset_account
            
        _logger.info(
            "Creating PEAS journal entry: %s transaction - Debit %s, Credit %s",
            self.transaction_type,
            debit_account.name,
            credit_account.name
        )
        
        # Instead of trying to create an invoice with the non-standard account types,
        # create a simple journal entry first
        journal_entry = self.env['account.move'].create({
            'journal_id': journal.id,
            'date': fields.Date.today(),
            'ref': f"Car {self.transaction_type.capitalize()} - {self.name}",
            'narration': f"Reference: {self.name}\nCar: {self.car_id.make} {self.car_id.model} ({self.car_id.year})\n{self.notes or ''}",
            'line_ids': [
                (0, 0, {
                    'name': f"{self.car_id.make} {self.car_id.model} ({self.car_id.year})",
                    'account_id': debit_account.id,
                    'debit': self.price,
                    'credit': 0.0,
                    'partner_id': partner.id,
                }),
                (0, 0, {
                    'name': f"{self.car_id.make} {self.car_id.model} ({self.car_id.year})",
                    'account_id': credit_account.id,
                    'debit': 0.0,
                    'credit': self.price,
                    'partner_id': partner.id,
                }),
            ],
        })
        
        _logger.info("Journal entry created successfully: %s", journal_entry.name)
        
        # Post the journal entry
        try:
            journal_entry.action_post()
            _logger.info("Journal entry posted successfully")
        except Exception as e:
            _logger.error("Error posting journal entry: %s", str(e))
            # Create a regular invoice as fallback if journal entry fails
            invoice_vals = self._prepare_invoice_vals()
            journal_entry = self.env['account.move'].create(invoice_vals)
            journal_entry.action_post()
            
        # Now create a matching invoice to display in the UI
        # This is purely for UI display and will reference the journal entry
        if self.transaction_type == 'buy':
            move_type = 'in_invoice'  # Vendor Bill
        else:
            move_type = 'out_invoice'  # Customer Invoice
            
        # Get standard account for invoice based on type
        std_account = self.env['account.account'].search([
            ('account_type', '=', 'income' if self.transaction_type == 'sell' else 'expense'),
            ('company_id', '=', self.company_id.id)
        ], limit=1)
        
        if not std_account:
            # If no standard account is found, log an error and find any valid account
            _logger.error("Could not find a standard %s account, searching for any valid account", 
                         'income' if self.transaction_type == 'sell' else 'expense')
            std_account = self.env['account.account'].search([
                ('company_id', '=', self.company_id.id),
                ('deprecated', '=', False)
            ], limit=1)
            
        if not std_account:
            raise UserError(_('No valid account found to create the invoice. Please configure your chart of accounts.'))
            
        std_account_id = std_account.id
        
        # Create a regular invoice that complies with account type validation
        # This will be used for UI display, while the actual accounting is handled by the journal entry
        invoice_vals = {
            'partner_id': partner.id,
            'move_type': move_type,
            'journal_id': journal.id,
            'invoice_date': fields.Date.today(),
            'narration': f"Reference: {self.name}\nCar: {self.car_id.make} {self.car_id.model} ({self.car_id.year})\n{self.notes or ''}\n\nPEAS Journal Entry: {journal_entry.name}",
            'invoice_line_ids': [(0, 0, {
                'name': f"{self.car_id.make} {self.car_id.model} ({self.car_id.year}) - {self.car_id.vin or ''} (PEAS Transaction - See {journal_entry.name})",
                'quantity': 1.0,
                'price_unit': self.price,
                'account_id': std_account_id,
            })],
        }
        
        _logger.info("Creating display invoice with account_id: %s", std_account_id)
        
        # Create and post the invoice with error handling
        try:
            # Verify once more that we have a valid account_id before creating the invoice
            if not std_account_id:
                raise UserError(_('Cannot create invoice: No valid account ID found'))
                
            _logger.info("Creating display invoice with account_id: %s (exists: %s)", 
                       std_account_id, bool(self.env['account.account'].browse(std_account_id).exists()))
                
            invoice = self.env['account.move'].create(invoice_vals)
            invoice.action_post()
        except Exception as e:
            _logger.error("Error creating display invoice: %s", str(e))
            # Return the journal entry as fallback
            return journal_entry
        
        return invoice

class CarOfferSequence(models.Model):
    _name = 'ir.sequence'
    _inherit = 'ir.sequence'
    
    @api.model
    def _create_car_offer_sequence(self):
        self.env['ir.sequence'].sudo().create({
            'name': 'Car Offer',
            'code': 'car.offer',
            'prefix': 'OFFER/',
            'padding': 4,
            'company_id': False,
        })
