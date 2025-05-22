# -*- coding: utf-8 -*-
{
    'name': 'Car Sales and Purchase',
    'version': '17.0.1.0.0',
    'summary': 'Manage car sales and purchases through connections',
    'author': '',
    'website': '',
    'category': 'Sales/Purchase',
    'depends': [
        'base', 
        'sale_management', 
        'purchase', 
        'account', 
        'peas_employee',
    ],
    'data': [
        'security/car_sales_security.xml',
        'security/ir.model.access.csv',
        'views/connection_views.xml',
        'views/car_views.xml',
        'views/offer_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
