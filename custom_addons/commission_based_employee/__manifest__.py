# -*- coding: utf-8 -*-
{
    'name': 'Commission_based_employee',
    'version': '17.0.1.0.0',
    'summary': """ Commission_based_employee Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'web', 'hr', 'hr_contract', 'hr_payroll', 'hr_payroll_account'],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_employee_form_views.xml",
    ],
    'assets': {
              'web.assets_backend': [
                  'commission_based_employee/static/src/**/*'
              ],
          },
    'application': False,
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
