# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PeasEmployeePayAdvance(models.TransientModel):
    _name = 'peas.employee.pay.advance'
    _description = 'Pay Advance to PEAS Employee'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, readonly=True)
    receivable_account_id = fields.Many2one('account.account', string='Receivable Account', 
                                           required=True, readonly=True)
    debit_account_id = fields.Many2one('account.account', string='Debit Account', 
                                      required=True, domain=[('account_type', 'not in', ['asset_receivable', 'liability_payable'])])
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True)
    amount = fields.Monetary(string='Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                 default=lambda self: self.env.company.currency_id, readonly=True)
    payment_date = fields.Date(string='Payment Date', required=True, default=fields.Date.context_today, readonly=True)
    memo = fields.Char(string='Memo', help="Internal note for the payment")

    @api.model
    def default_get(self, fields_list):
        res = super(PeasEmployeePayAdvance, self).default_get(fields_list)
        
        # Get employee from context
        employee_id = self.env.context.get('active_id')
        employee = self.env['hr.employee'].browse(employee_id)
        
        if not employee or not employee.exists():
            raise UserError(_("Employee not found."))
            
        if not employee.is_peas_employee:
            raise UserError(_("This wizard is only available for PEAS employees."))
            
        if not employee.receivable_account_id or not employee.journal_id:
            raise UserError(_("Employee does not have required accounting configuration."))
            
        res.update({
            'employee_id': employee.id,
            'receivable_account_id': employee.receivable_account_id.id,
            'journal_id': employee.journal_id.id,
        })
        
        return res
    
    def action_pay_advance(self):
        """Create journal entry for the advance payment"""
        self.ensure_one()
        
        if self.amount <= 0:
            raise ValidationError(_("Amount must be positive."))
            
        # Prepare journal entry
        move_vals = {
            'journal_id': self.journal_id.id,
            'date': self.payment_date,
            'ref': _('Advance: %s') % self.employee_id.name,
            'move_type': 'entry',
        }
        
        # Create line items
        line_vals = [
            # Debit line (using the selected debit account)
            {
                'name': self.memo or _('Advance to %s') % self.employee_id.name,
                'account_id': self.debit_account_id.id,
                'debit': self.amount,
                'credit': 0.0,
                'partner_id': self.employee_id.work_contact_id.id or self.employee_id.customer_id.id,
            },
            # Credit line (using employee's receivable account)
            {
                'name': self.memo or _('Advance to %s') % self.employee_id.name,
                'account_id': self.receivable_account_id.id,
                'debit': 0.0,
                'credit': self.amount,
                'partner_id': self.employee_id.work_contact_id.id or self.employee_id.customer_id.id,
            }
        ]
        move_vals['line_ids'] = [(0, 0, line) for line in line_vals]
        
        # Create and post the journal entry
        move = self.env['account.move'].create(move_vals)
        # Removed: move.action_post() - To keep the entry in draft state
        
        # Show success message and return to employee form
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Advance payment of %s recorded for %s') % (
                    self.amount, self.employee_id.name),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
