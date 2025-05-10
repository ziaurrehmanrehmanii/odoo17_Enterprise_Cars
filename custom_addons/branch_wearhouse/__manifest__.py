# -*- coding: utf-8 -*-
{
    'name': 'Branch_wearhouse',
    'version': '17.0.1.0.0',
    'summary': """ Branch_wearhouse Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'web', 'stock'],
    "data": [
        "security/ir.model.access.csv",
    ],
    'assets': {
              'web.assets_backend': [
                  'branch_wearhouse/static/src/**/*'
              ],
          },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
