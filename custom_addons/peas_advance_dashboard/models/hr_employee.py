from odoo import models, fields, api, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    advance_payment_count = fields.Integer(
        string="Advance Payments",
        compute='_compute_advance_payment_count'
    )

    def _compute_advance_payment_count(self):
        for employee in self:
            employee.advance_payment_count = self.env['account.move'].search_count([
                ('partner_id', 'in', [employee.vendor_partner_id.id, employee.customer_partner_id.id]),
                ('move_type', '=', 'in_invoice'),
                ('invoice_line_ids.name', 'ilike', 'advance payment'),
            ])

    def action_view_advance_payments(self):
        self.ensure_one()
        domain = [
            ('partner_id', 'in', [self.vendor_partner_id.id, self.customer_partner_id.id]),
            ('move_type', '=', 'in_invoice'),
            ('invoice_line_ids.name', 'ilike', 'advance payment'),
        ]
        return {
            'name': _('Advance Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {'default_partner_id': self.vendor_partner_id.id},
        }