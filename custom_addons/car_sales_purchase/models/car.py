# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class CarDetails(models.Model):
    _name = 'car.details'
    _description = 'Car Details'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Description', required=True, tracking=True)
    make = fields.Char('Make', required=True, tracking=True)
    model = fields.Char('Model', required=True, tracking=True)
    year = fields.Integer('Year', required=True, tracking=True)
    color = fields.Char('Color')
    
    # Condition options
    condition = fields.Selection([
        ('new', 'New'),
        ('used', 'Used'),
        ('certified', 'Certified Pre-Owned'),
        ('salvage', 'Salvage'),
        ('parts', 'Parts Only')
    ], string='Condition', required=True, default='used', tracking=True)
    
    # Technical details
    vin = fields.Char('VIN', tracking=True)
    mileage = fields.Float('Mileage', tracking=True)
    fuel_type = fields.Selection([
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('other', 'Other')
    ], string='Fuel Type', default='petrol')
    transmission = fields.Selection([
        ('automatic', 'Automatic'),
        ('manual', 'Manual'),
        ('semi', 'Semi-Automatic')
    ], string='Transmission', default='automatic')
    
    # Transaction details
    transaction_type = fields.Selection([
        ('buy', 'Buy'),
        ('sell', 'Sell')
    ], string='Transaction Type', required=True, tracking=True)
    connection_id = fields.Many2one('car.connection', string='Connection', required=True, tracking=True)
    connection_name = fields.Char(related='connection_id.name', string='Connection Name', store=True)
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    # Financial details
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    asking_price = fields.Monetary(string='Asking Price', currency_field='currency_id', tracking=True)
    expected_price = fields.Monetary(string='Expected Price', currency_field='currency_id', tracking=True)
    final_price = fields.Monetary(string='Final Price', currency_field='currency_id', tracking=True, readonly=True)
    
    # Status and tracking
    state = fields.Selection([
        ('draft', 'Draft'),
        ('negotiation', 'In Negotiation'),
        ('offer_accepted', 'Offer Accepted'),
        ('invoiced', 'Invoiced'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    active = fields.Boolean(default=True)
    notes = fields.Text('Notes')
    
    offer_ids = fields.One2many('car.offer', 'car_id', string='Offers')
    offer_count = fields.Integer(compute='_compute_offer_count', string='Offers')
    accepted_offer_id = fields.Many2one('car.offer', string='Accepted Offer', compute='_compute_accepted_offer', store=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', copy=False)
    
    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for car in self:
            car.offer_count = len(car.offer_ids)
    
    @api.depends('offer_ids.state')
    def _compute_accepted_offer(self):
        for car in self:
            accepted_offer = car.offer_ids.filtered(lambda o: o.state == 'accepted')
            car.accepted_offer_id = accepted_offer[0] if accepted_offer else False

    def action_view_offers(self):
        self.ensure_one()
        return {
            'name': _('Offers'),
            'type': 'ir.actions.act_window',
            'res_model': 'car.offer',
            'view_mode': 'tree,form',
            'domain': [('car_id', '=', self.id)],
            'context': {'default_car_id': self.id, 'default_transaction_type': self.transaction_type},
        }
    
    def action_create_offer(self):
        self.ensure_one()
        # Try to find a PEAS employee for the current user
        peas_employee = self.env['hr.employee'].search([
            ('user_id', '=', self.env.user.id),
            ('is_peas_employee', '=', True)
        ], limit=1)
        
        return {
            'name': _('Create Offer'),
            'type': 'ir.actions.act_window',
            'res_model': 'car.offer',
            'view_mode': 'form',
            'context': {
                'default_car_id': self.id,
                'default_transaction_type': self.transaction_type,
                'default_currency_id': self.currency_id.id,
                'default_employee_id': peas_employee.id if peas_employee else False,
            },
            'target': 'new',
        }
    
    def action_set_to_negotiation(self):
        self.write({'state': 'negotiation'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_view_offer_invoice(self):
        """View invoice from the accepted offer"""
        self.ensure_one()
        if self.accepted_offer_id and self.accepted_offer_id.invoice_id:
            return self.accepted_offer_id.action_view_invoice()
        elif self.invoice_id:
            return {
                'name': _('Invoice'),
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': self.invoice_id.id,
                'target': 'current',
            }
        else:
            raise UserError(_('No invoice found for this car.'))
