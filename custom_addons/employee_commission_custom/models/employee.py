# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_type = fields.Selection([
        ('commission', 'Commission-Based'),
        ('commission_salary', 'Commission + Salary'),
        ('salary', 'Salary-Only'),
        ('pase', 'PASE'),  # Added new employee type
    ], string='Employee Type', required=True, default='salary')

    current_salary = fields.Monetary(string="Current Salary")
    current_commission_percentage = fields.Float(string="Current Commission (%)")
    commission_history_ids = fields.One2many('employee.commission.history', 'employee_id', string="Commission History")
    journal_id = fields.Many2one('account.journal', string="Associated Journal", readonly=True)

    total_commission = fields.Monetary(string="Total Commission", compute="_compute_total_commission", store=True)
    current_month_commission = fields.Monetary(string="Current Month Commission", compute="_compute_current_month_commission")
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    @api.model
    def create(self, vals):
        employee = super(HrEmployee, self).create(vals)
        
        # If employee is PASE type, create journal and add to group
        if employee.employee_type == 'pase':
            self._create_journal_for_pase(employee)
            self._add_user_to_pease_group(employee)
            
        return employee
    
    def write(self, vals):
        result = super(HrEmployee, self).write(vals)
        
        # Check if employee type was changed to PASE
        if vals.get('employee_type') == 'pase':
            for employee in self:
                if not employee.journal_id:
                    self._create_journal_for_pase(employee)
                self._add_user_to_pease_group(employee)
                
        return result
    
    def _create_journal_for_pase(self, employee):
        """Create an account journal for PASE employee"""
        journal_obj = self.env['account.journal']
        
        # Avoid duplicating journals
        existing_journal = journal_obj.search([
            ('name', '=', f"{employee.name} Journal"),
            ('company_id', '=', employee.company_id.id)
        ], limit=1)
        
        if not existing_journal:
            journal = journal_obj.sudo().create({
                'name': f"{employee.name} Journal",
                'code': f"P{employee.id:04d}"[:5],  # Limit to 5 chars
                'type': 'general',
                'company_id': employee.company_id.id,
            })
            
            # Link the journal to the employee
            employee.sudo().journal_id = journal.id
    
    def _add_user_to_pease_group(self, employee):
        """Add employee's user to PEASE group"""
        if not employee.user_id:
            return
            
        # Get PEASE group
        pease_group = self.env.ref('employee_commission_custom.group_pease')
        
        # Add user to PEASE group
        if pease_group and employee.user_id:
            pease_group.sudo().write({'users': [(4, employee.user_id.id)]})

    @api.depends('commission_history_ids.amount')
    def _compute_total_commission(self):
        for employee in self:
            employee.total_commission = sum(history.amount for history in employee.commission_history_ids)

    def _compute_current_month_commission(self):
        today = date.today()
        current_month = today.month
        current_year = today.year
        
        for employee in self:
            current_month_records = employee.commission_history_ids.filtered(
                lambda r: r.start_date and r.start_date.month == current_month and r.start_date.year == current_year
            )
            employee.current_month_commission = sum(record.amount for record in current_month_records)


class EmployeeCommissionHistory(models.Model):
    _name = 'employee.commission.history'
    _description = 'Employee Commission History'
    _order = 'start_date desc'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, ondelete='cascade')
    percentage = fields.Float(string="Commission %", required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date")
    amount = fields.Monetary(string="Commission Amount")
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    notes = fields.Text(string="Notes")