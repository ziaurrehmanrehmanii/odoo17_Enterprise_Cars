# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'
    
    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None, count=False):
        # Get the user making the call
        user = self.env.user
        _logger.info("Current User: %s", user.name)
        _logger.info("Initial Args: %s", domain)

        if user.has_group('peas_employee.group_peas_employee_user'):
            # Get Car Sales & Purchase menu and all its children
            car_sales_menu = self.env.ref('car_sales_purchase.menu_car_sales_purchase_root', False)
            
            if car_sales_menu:
                # Find all child menus of the car_sales_menu
                all_child_menus = self.search([('parent_id', 'child_of', car_sales_menu.id)])
                allowed_menu_ids = [car_sales_menu.id] + all_child_menus.ids
                
                # Show only car_sales_menu and its children
                domain = expression.AND([domain, [('id', 'in', allowed_menu_ids)]])
                _logger.info("Updated Args: %s", domain)
        
        # Call the super method
        result = super()._search(
            domain,
            offset=offset,
            limit=limit,
            order=order,
            access_rights_uid=access_rights_uid,
            # count=count
        )
        
        _logger.info("Search Result: %s", result)
        return result