# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    # Add any custom fields you need for branches
    branch_user_ids = fields.Many2many(
        'res.users',
        'branch_company_users_rel',
        'company_id',
        'user_id',
        string='Branch Users'
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        companies = super(ResCompany, self).create(vals_list)
        for company in companies:
            if company.parent_id:
                # This is a branch (has a parent company)
                # Check if warehouse already exists for this company
                existing_warehouse = self.env['stock.warehouse'].sudo().search([
                    ('company_id', '=', company.id)
                ], limit=1)
                
                if existing_warehouse:
                    _logger.info(f"Warehouse '{existing_warehouse.name}' already exists for company '{company.name}'")
                    warehouse = existing_warehouse
                else:
                    warehouse_vals = {
                        'name': company.name,
                        'code': company.name[:5].upper(),  # Create a code from company name
                        'company_id': company.id,
                    }
                    try:
                        warehouse = self.env['stock.warehouse'].sudo().create(warehouse_vals)
                        _logger.info(f"Warehouse '{warehouse.name}' created for branch company '{company.name}'")
                    except Exception as e:
                        _logger.error(f"Failed to create warehouse for company {company.name}: {str(e)}")
                        continue
                
                # Set as default warehouse for inventory operations (whether new or existing)
                try:
                    self.env['ir.property'].sudo().create({
                        'name': 'property_stock_inventory',
                        'company_id': company.id,
                        'value_reference': f'stock.warehouse,{warehouse.id}',
                        'field_id': self.env['ir.model.fields'].search([
                            ('model', '=', 'res.company'),
                            ('name', '=', 'property_stock_inventory')
                        ]).id,
                    })
                except Exception as e:
                    _logger.error(f"Failed to set default warehouse for company {company.name}: {str(e)}")
        
        return companies