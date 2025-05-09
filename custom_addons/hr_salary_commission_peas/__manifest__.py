# -*- coding: utf-8 -*-
{
    'name': "HR Salary and Commission Peas",

    'summary': "A module to manage HR salary and commission for Peas Users",

    'description': """
        This module allows you to manage the salary and commission structure for Peas users in Odoo.
        It includes features for creating and managing employee types, commission history,
        and associated Account Types. such as PASE Vendor and PASE Customer.
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Customization',
    'version': '0.1',

    'depends': [
    'base', 
    'hr', 
    'hr_payroll', 
    'hr_contract', 
    'account', 
    'sale_management', 
    'purchase', 
    'contacts'
],

    'data': [
        'security/security.xml',
        'views/employee_views.xml',
        'views/partner_views.xml',  # Added new partner view
        'views/templates.xml',
        'security/ir.model.access.csv',
    ],
    
    'demo': [
        'demo/demo.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}