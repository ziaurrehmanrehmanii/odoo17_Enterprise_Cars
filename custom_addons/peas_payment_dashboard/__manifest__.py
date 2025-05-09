# -*- coding: utf-8 -*-
{
    'name': "PEAS Payment Dashboard",
    'summary': """
        Dashboard for PEAS user payments and tracking
    """,
    'description': """
        This module provides a dashboard for tracking payments to PEAS users,
        including salary, commission, and advance payments.
    """,
    'author': "Your Company",
    'website': "https://www.yourcompany.com",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': [
        'base',
        'hr', 
        'account',
        'hr_salary_commission_peas',  # Added dependency
        'web',
    ],
 'data': [
    'views/peas_dashboard_views.xml',
    'views/peas_payment_views.xml',
    'security/ir.model.access.csv',
 ],
'assets': {
    'web.assets_backend': [
        'peas_payment_dashboard/static/src/css/dashboard.css',
        'peas_payment_dashboard/static/src/js/dashboard.js',
    ],
    'web.assets_qweb': [
        'peas_payment_dashboard/static/src/xml/dashboard_templates.xml',
    ],
},
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
}