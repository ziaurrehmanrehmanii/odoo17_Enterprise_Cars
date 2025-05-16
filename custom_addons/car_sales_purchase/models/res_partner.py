# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

 
class ResPartner(models.Model):
    _inherit = 'res.partner'
 
    _rec_name = 'name'
    _description = 'Connection for Car Sales and Purchase'
    _order = 'name asc'
    
    # add name field to the model
    name = fields.Char(string='Name', required=True, help="Full name of the partner")
    phone = fields.Char(string='Phone', help="Primary phone number of the partner")
    email = fields.Char(string='Email', help="Primary email address of the partner")
    address = fields.Text(string='Address', help="Physical address of the partner")
    user_id = fields.Many2one('res.users', string='User', help="User associated with this partner")
    car_ids = fields.One2many(
        'product.template', 
        'car_owner', 
        string='Cars Owned', 
        help="List of cars owned by this partner"
    )
    is_customer = fields.Boolean(string='Is Customer', default=False, help="Indicates if this partner is a customer")
    is_supplier = fields.Boolean(string='Is Supplier', default=False, help="Indicates if this partner is a supplier")
