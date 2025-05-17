# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'
    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # If user is in peas_employee group only and not in admin/manager groups
        user = self.env.user
        _logger.info("Current User:::::::::::::::::::::::::::::::::::::::::::::::::::::::::: %s", user.name)
        _logger.info("Initial Args:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: %s", args)

        if user.has_group('peas_employee.group_peas_employee_user'):
            # Get Car Sales & Purchase menu ID
            car_sales_menu = self.env.ref('car_sales_purchase.menu_car_sales_purchase_root', False)
            _logger.info("Car Sales & Purchase Menu::::::::::::::::::::::::::::::::::::::::::::::::::::: %s", car_sales_menu.id if car_sales_menu else "Not Found")
            
            if car_sales_menu:
                # Only show Car Sales & Purchase menu at the root level
                args = expression.AND([args, [('id', '=', car_sales_menu.id)]])
                _logger.info("Updated Args::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: %s", args)
        
        # Use named parameters to avoid positional argument count issues
        result = super()._search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            access_rights_uid=access_rights_uid
        )
        _logger.info("Search Result:::::::::::::::::::::::::::::::::::::::::::::::::::: %s", result)
        return result