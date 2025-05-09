# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from psycopg2.errors import UndefinedColumn
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # Define fields with proper schema updates
    employee_id = fields.Many2one('hr.employee', string="Related Employee")
    is_employee_vendor = fields.Boolean(string="Is Employee Vendor", default=False)
    is_employee_customer = fields.Boolean(string="Is Employee Customer", default=False)
    
    def name_get(self):
        """Override name_get to show employee status on partner records"""
        try:
            result = super(ResPartner, self).name_get()
            
            # Check if fields exist in database to avoid errors
            self.env.cr.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'res_partner' AND column_name IN ('is_employee_vendor', 'is_employee_customer')")
            existing_fields = {r[0] for r in self.env.cr.fetchall()}
            
            if 'is_employee_vendor' not in existing_fields or 'is_employee_customer' not in existing_fields:
                _logger.warning("Partner fields not yet created in database - skipping custom name_get")
                return result
            
            new_result = []
            for partner_id, name in result:
                partner = self.browse(partner_id)
                
                if partner.is_employee_vendor:
                    name = f"{name} [Employee Vendor]"
                elif partner.is_employee_customer:
                    name = f"{name} [Employee Customer]"
                    
                new_result.append((partner_id, name))
                
            return new_result
        except Exception as e:
            _logger.error(f"Error in partner name_get: {str(e)}")
            return super(ResPartner, self).name_get()