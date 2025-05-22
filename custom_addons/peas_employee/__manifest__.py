# -*- coding: utf-8 -*-
{
    'name': 'Peas_employee',
    'version': '17.0.1.0.0',
    'summary': """ Peas_employee Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'web', 'hr','account','sale_management','crm','stock','hr_expense','hr_payroll','purchase','car_sales_purchase'],
"data": [
    "security/ir.model.access.csv",
    "security/peas_employee_security.xml",
    "security/ir_rule.xml",  # Added this line
    "views/peas_employee_pay_advance_views.xml",  # THIS FIRST
    "views/hr_employee_views.xml"                           # THEN THIS
],
    'assets': {
              'web.assets_backend': [
                  'peas_employee/static/src/**/*'
              ],
          },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
