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
        if user.has_group('peas_employee.group_peas_employee_user'):
            # Get Contacts menu ID
            contacts_menu = self.env.ref('contacts.menu_contacts', False)
            if contacts_menu:
                # Only show contacts menu at the root level
                root_menu_args = [('parent_id', '=', False), ('id', '!=', contacts_menu.id)]
                root_menus = super()._search(root_menu_args)
                # Add these menus to the restriction list
                args = expression.AND([args, [('id', 'not in', root_menus)]])
        
        # Use named parameters to avoid positional argument count issues
        return super()._search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            access_rights_uid=access_rights_uid
        )