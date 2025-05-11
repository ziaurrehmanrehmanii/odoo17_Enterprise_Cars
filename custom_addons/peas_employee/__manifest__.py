# -*- coding: utf-8 -*-
{
    'name': 'Peas_employee',
    'version': '17.0.1.0.0',
    'summary': """ Peas_employee Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'web', 'hr','account','sale_management','crm','stock','hr_expense','hr_payroll','purchase'],
    "data": [
        "views/hr_employee_views.xml"
    ],
    'assets': {
              'web.assets_backend': [
                  'peas_employee/static/src/**/*'
              ],
          },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
