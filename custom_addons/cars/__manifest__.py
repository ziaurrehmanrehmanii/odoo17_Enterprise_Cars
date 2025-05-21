# -*- coding: utf-8 -*-
{
    'name': 'Cars',
    'version': '17.0.1.0.0',
    'summary': """ Cars Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'web','peas_employee','car_sales_purchase'],
    "data": [
        "views/cars_menue_views.xml"
    ],
    'assets': {
              'web.assets_backend': [
                  'cars/static/src/**/*'
              ],
          },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
