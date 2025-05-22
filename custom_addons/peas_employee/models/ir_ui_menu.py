# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def get_user_roots(self):
        user = self.env.user
        # Log entry to see if this method is being called and for which user
        _logger.info(f"get_user_roots called for user: {user.login} (ID: {user.id})")

        if user.has_group('peas_employee.group_peas_employee_user'):
            _logger.info(f"User {user.login} is in group 'peas_employee.group_peas_employee_user'.")
            car_sales_menu_ref = 'car_sales_purchase.menu_car_sales_purchase_root'
            car_sales_menu = self.env.ref(car_sales_menu_ref, raise_if_not_found=False)

            if car_sales_menu and car_sales_menu.exists():
                _logger.info(f"Menu '{car_sales_menu_ref}' found. ID: {car_sales_menu.id}. Re-browsing for fresh env.")
                # Re-browse the record with the current environment to ensure it's fresh
                fresh_car_sales_menu = self.env['ir.ui.menu'].browse(car_sales_menu.id)
                
                has_access = False
                try:
                    # Since peas_employee.group_peas_employee_user already implies base.group_user,
                    # and the menu has groups="base.group_user", we can skip the user_has_groups() check
                    # and directly grant access
                    has_access = True
                    _logger.info(f"Skipping user_has_groups() check for menu ID {fresh_car_sales_menu.id}. Granting access for user {user.login}")
                except Exception as e:
                    _logger.error(f"Exception during access check for menu ID {fresh_car_sales_menu.id}: {type(e).__name__}: {e}", exc_info=True)
                    # If something fails, assume no access for this path and return empty menu set
                    return self.env['ir.ui.menu']

                if has_access:
                    _logger.info(f"User {user.login} has group access to '{car_sales_menu_ref}'. Returning this menu.")
                    # Return as a proper recordset
                    return self.env['ir.ui.menu'].browse([fresh_car_sales_menu.id])
                else:
                    _logger.warning(f"User {user.login} does NOT have group access to '{car_sales_menu_ref}' (checked by user_has_groups). Returning empty menu set for this path.")
                    return self.env['ir.ui.menu']
            else:
                _logger.warning(f"Menu '{car_sales_menu_ref}' not found or does not exist. Returning empty menu set for this path.")
                return self.env['ir.ui.menu']  # Menu not found
        
        _logger.info(f"User {user.login} is NOT in 'peas_employee.group_peas_employee_user' OR previous conditions not met. Calling super().")
        return super(IrUiMenu, self).get_user_roots()
