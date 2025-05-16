# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    _rec_name = 'car'
    _description = 'Product Template for Car Sales and Purchase'
    _order = 'name asc'
    # Add fields specific to car sales and purchase
    
    car = fields.Boolean(string="Is a Car", default=False)
    car_brand = fields.Char(string="Car Brand")
    car_year = fields.Integer(string="Car Year")
    car_color = fields.Char(string='Car Color', help="Color of the car")
    car_vin = fields.Char(string='VIN', help="Vehicle Identification Number of the car")
    car_price = fields.Float(string="Car Price")
    car_mileage = fields.Float(string='Car Mileage', help="Mileage of the car in kilometers")
    car_description = fields.Text(string='Car Description', help="Detailed description of the car")
    car_image = fields.Binary(string='Car Image', help="Image of the car")
    car_is_available = fields.Boolean(string='Is Available', default=True, help="Indicates if the car is available for sale")
    car_sale_date = fields.Date(string='Sale Date', help="Date when the car was sold")
    car_purchase_date = fields.Date(string='Purchase Date', help="Date when the car was purchased")
    car_owner = fields.Many2one('res.partner', string='Car Owner', help="Owner of the car")
    car_purchase_price = fields.Float(string='Purchase Price', help="Price at which the car was purchased")
    car_sale_price = fields.Float(string='Sale Price', help="Price at which the car was sold")
    
    @api.onchange('car')
    def _onchange_car(self):
        if not self.car:
            self.car_brand = False
            self.car_year = False
            self.car_price = 0.0
