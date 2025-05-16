# -*- coding: utf-8 -*-
{
    'name': 'Car Sales and Purchase',
    'version': '1.0',
    'summary': 'Manage car sales and purchases',
    'description': """
        This module allows you to manage car sales and purchases.
    """,
    'category': 'Sales',
    'author': 'Your Name',
    'website': '',
    'depends': [
        'base',
        'product',  # Added product dependency
        'sale',     # Added sale dependency for sales functionality
    ],
    "data": [
        "views/menu_views.xml",
        "views/res_partner_views.xml",
        "views/product_template_views.xml",
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
