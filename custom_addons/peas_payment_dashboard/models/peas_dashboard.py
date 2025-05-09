# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PeasDashboard(models.Model):
    _name = 'peas.dashboard'
    _description = 'PEAS User Dashboard'
    
    name = fields.Char(related='employee_id.name', string='Name')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, domain=[('is_peas', '=', True)])
    payment_count = fields.Integer(compute='_compute_payment_count', string='Number of Payments')
    total_payments = fields.Monetary(compute='_compute_total_payments', string='Total Payments')
    currency_id = fields.Many2one('res.currency', related='employee_id.currency_id')
    
    @api.depends('employee_id')
    def _compute_payment_count(self):
        for record in self:
            record.payment_count = self.env['peas.payment'].search_count([
                ('employee_id', '=', record.employee_id.id)
            ])
    
    @api.depends('employee_id')
    def _compute_total_payments(self):
        for record in self:
            payments = self.env['peas.payment'].search([
                ('employee_id', '=', record.employee_id.id)
            ])
            record.total_payments = sum(payment.amount for payment in payments)
    
    def action_view_payments(self):
        self.ensure_one()
        return {
            'name': _('Payments for %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'peas.payment',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.employee_id.id)],
            'context': {'default_employee_id': self.employee_id.id},
        }
    
    @api.model
    def load_peas_employees(self):
        """Manual method to load PEAS employees into the dashboard"""
        # Get all employees marked as PEAS
        peas_employees = self.env['hr.employee'].search([('is_peas', '=', True)])
        
        # Get existing dashboard entries
        existing_entries = self.search([])
        existing_employee_ids = existing_entries.mapped('employee_id.id')
        
        # Create dashboard entries for new PEAS employees
        for employee in peas_employees:
            if employee.id not in existing_employee_ids:
                self.create({'employee_id': employee.id})
        
        return True


# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

class PeasDashboard(models.Model):
    _name = 'peas.dashboard'
    _description = 'PEAS User Dashboard'
    
    name = fields.Char(related='employee_id.name', string='Name')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, domain=[('is_peas', '=', True)])
    payment_count = fields.Integer(compute='_compute_payment_count', string='Number of Payments')
    total_payments = fields.Monetary(compute='_compute_total_payments', string='Total Payments')
    currency_id = fields.Many2one('res.currency', related='employee_id.currency_id')
    
    @api.depends('employee_id')
    def _compute_payment_count(self):
        for record in self:
            record.payment_count = self.env['peas.payment'].search_count([
                ('employee_id', '=', record.employee_id.id)
            ])
    
    @api.depends('employee_id')
    def _compute_total_payments(self):
        for record in self:
            payments = self.env['peas.payment'].search([
                ('employee_id', '=', record.employee_id.id)
            ])
            record.total_payments = sum(payment.amount for payment in payments)
    
    def action_view_payments(self):
        self.ensure_one()
        return {
            'name': _('Payments for %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'peas.payment',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.employee_id.id)],
            'context': {'default_employee_id': self.employee_id.id},
        }
    
    @api.model
    def load_peas_employees(self):
        """Load all employees marked as PEAS users"""
        # Find PEAS employees
        peas_employees = self.env['hr.employee'].search([('is_peas', '=', True)])
        
        # Get existing dashboard entries
        existing_employees = self.search([]).mapped('employee_id.id')
        
        # Create dashboard entries for PEAS employees that don't have one
        for employee in peas_employees:
            if employee.id not in existing_employees:
                self.create({'employee_id': employee.id})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
    # Auto-load PEAS employees on install
    @api.model
    def init(self):
        self.load_peas_employees()


class PeasPayment(models.Model):
    _name = 'peas.payment'
    _description = 'PEAS User Payment'
    _order = 'payment_date desc'
    
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, 
                       default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, 
                                 domain=[('is_peas', '=', True)])
    payment_date = fields.Date(string='Payment Date', default=fields.Date.today)
    amount = fields.Monetary(string='Amount', required=True)
    currency_id = fields.Many2one('res.currency', related='employee_id.currency_id')
    payment_type = fields.Selection([
        ('advance', 'Advance Payment'),
        ('commission', 'Commission Payment'),
        ('salary', 'Salary Payment'),
        ('other', 'Other Payment')
    ], string='Payment Type', default='advance')
    description = fields.Text(string='Description')
    related_invoice_id = fields.Many2one('account.move', string='Related Invoice')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('peas.payment') or _('New')
        return super(PeasPayment, self).create(vals)
    
    def action_post(self):
        for record in self:
            record.state = 'posted'
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
    
    def action_draft(self):
        for record in self:
            record.state = 'draft'
    
    def action_print_report(self):
        return self.env.ref('peas_payment_dashboard.action_report_peas_payment').report_action(self)
    
    @api.model
    def get_dashboard_data(self):
        """Method called by JS to get dashboard data"""
        # Get total PEAS users
        peas_users_count = self.env['hr.employee'].search_count([('is_peas', '=', True)])
        
        # Get payment statistics
        payments = self.env['peas.payment'].search([
            ('state', '!=', 'cancelled')
        ])
        total_payment_amount = sum(payment.amount for payment in payments)
        
        # Get recent payments
        recent_payments = self.env['peas.payment'].search([
            ('state', '!=', 'cancelled')
        ], limit=5, order='payment_date desc')
        
        # Format data for the dashboard
        formatted_payments = []
        for payment in recent_payments:
            formatted_payments.append({
                'id': payment.id,
                'name': payment.name,
                'employee_name': payment.employee_id.name,
                'payment_date': payment.payment_date.strftime('%Y-%m-%d'),
                'amount': payment.amount,
                'state': payment.state,
            })
        
        return {
            'total_peas_users': peas_users_count,
            'total_payments': len(payments),
            'total_payment_amount': total_payment_amount,
            'recent_payments': formatted_payments,
        }