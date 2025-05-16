# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Connection(models.Model):
    _name = 'car.connection'
    _description = 'Car Connection'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Name', required=True, tracking=True)
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    city = fields.Char('City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char('ZIP')
    country_id = fields.Many2one('res.country', string='Country')
    email = fields.Char('Email')
    phone = fields.Char('Phone')
    mobile = fields.Char('Mobile')
    
    notes = fields.Text('Notes')
    active = fields.Boolean(default=True)
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    car_count = fields.Integer(compute='_compute_car_count', string='Cars')
    buy_car_ids = fields.One2many('car.details', 'connection_id', domain=[('transaction_type', '=', 'buy')], string='Buy Cars')
    sell_car_ids = fields.One2many('car.details', 'connection_id', domain=[('transaction_type', '=', 'sell')], string='Sell Cars')
    
    @api.depends('buy_car_ids', 'sell_car_ids')
    def _compute_car_count(self):
        for record in self:
            record.car_count = len(record.buy_car_ids) + len(record.sell_car_ids)
    
    def action_view_cars(self):
        self.ensure_one()
        return {
            'name': _('Cars'),
            'type': 'ir.actions.act_window',
            'res_model': 'car.details',
            'view_mode': 'tree,form,kanban',
            'domain': [('connection_id', '=', self.id)],
            'context': {'default_connection_id': self.id},
        }
