# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    def action_view_car_connections(self):
        """
        This method opens a view to show car connections related to this partner.
        """
        self.ensure_one()
        return {
            'name': _('Car Connections'),
            'type': 'ir.actions.act_window',
            'res_model': 'car.connection',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
