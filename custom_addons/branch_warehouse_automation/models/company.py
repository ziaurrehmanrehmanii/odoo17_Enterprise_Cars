# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = 'res.company'

    # Add a one2many field to see warehouses linked to this company
    warehouse_ids = fields.One2many('stock.warehouse', 'company_id', string='Warehouses')
    
    @api.model
    def create(self, vals):
        # Create the company
        company = super(ResCompany, self).create(vals)
        
        # If this company has a parent (it's a branch), create a warehouse
        if company.parent_id:
            # Check if company already has warehouses
            existing_warehouses = self.env['stock.warehouse'].sudo().search([('company_id', '=', company.id)])
            
            if not existing_warehouses:
                # Create a warehouse for the branch company
                code = company.name[:5].upper() if len(company.name) >= 5 else company.name.upper()
                code = code.replace(' ', '')  # Remove spaces for warehouse code
                
                try:
                    # Use sudo() to create the warehouse with admin privileges
                    warehouse = self.env['stock.warehouse'].sudo().create({
                        'name': f"{company.name} Warehouse",
                        'code': code,
                        'company_id': company.id,
                    })
                    
                    _logger.info(f"Warehouse '{warehouse.name}' created for branch company '{company.name}'.")
                except Exception as e:
                    _logger.error(f"Failed to create warehouse for company {company.name}: {str(e)}")
        
        return company