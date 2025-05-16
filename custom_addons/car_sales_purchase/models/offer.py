# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class CarOffer(models.Model):
    _name = 'car.offer'
    _description = 'Car Offer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'
    
    name = fields.Char('Reference', readonly=True, copy=False, default='New')
    car_id = fields.Many2one('car.details', string='Car', required=True, ondelete='cascade')
    transaction_type = fields.Selection(related='car_id.transaction_type', string='Transaction Type', store=True)
    connection_id = fields.Many2one(related='car_id.connection_id', string='Connection', store=True)
    
    date = fields.Datetime('Offer Date', default=fields.Datetime.now, required=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    price = fields.Monetary(string='Offer Price', currency_field='currency_id', required=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', tracking=True)
    
    notes = fields.Text('Notes')
    
    @api.model_create_multi
    def create(self, vals_list):
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
        
        # Create invoice based on transaction type
        invoice_vals = self._prepare_invoice_vals()
        invoice = self.env['account.move'].create(invoice_vals)
        
        # Post the invoice
        invoice.action_post()
        
        # Link invoice to the car
        self.car_id.write({
            'invoice_id': invoice.id,
            'state': 'invoiced'
        })
        
        # Update offer state
        self.write({'state': 'accepted'})
        
        return {
            'name': _('Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
        }
    
    def _prepare_invoice_vals(self):
        self.ensure_one()
        
        journal = self.env['account.journal'].search([
            ('type', '=', 'sale' if self.transaction_type == 'sell' else 'purchase'),
            ('company_id', '=', self.company_id.id)
        ], limit=1)
        
        if not journal:
            raise UserError(_('No journal found for %s transactions.') % self.transaction_type)
            
        partner = self.connection_id
        if not partner:
            raise UserError(_('No connection defined for this car.'))
        
        # Determine move type
        if self.transaction_type == 'sell':
            move_type = 'out_invoice'  # Customer Invoice
            account_id = self.env['account.account'].search([
                ('account_type', '=', 'income'),
                ('company_id', '=', self.company_id.id)
            ], limit=1).id
        else:  # buy
            move_type = 'in_invoice'  # Vendor Bill
            account_id = self.env['account.account'].search([
                ('account_type', '=', 'expense'),
                ('company_id', '=', self.company_id.id)
            ], limit=1).id
        
        invoice_vals = {
            'partner_id': partner.id,
            'move_type': move_type,
            'journal_id': journal.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': f"{self.car_id.make} {self.car_id.model} ({self.car_id.year}) - {self.car_id.vin or ''}",
                'quantity': 1.0,
                'price_unit': self.price,
                'account_id': account_id,
            })],
            'narration': f"Reference: {self.name}\n{self.notes or ''}",
        }
        
        return invoice_vals

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
