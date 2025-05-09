# -*- coding: utf-8 -*-
{
    'name': "PEAS Advance Dashboard",
    'summary': "Dashboard listing PEAS employees and their advance payments",
    'description': """
        This module provides a dashboard that lists only PEAS employees.
        Clicking a PEAS employee shows a list of their advance payments.
    """,
    'author': "Your Company",
    'website': "https://www.yourcompany.com",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': [
        'base',
        'hr',
        'account',
        'hr_salary_commission_peas',
    ],
    'data': [
        'views/peas_dashboard_views.xml',
        # Add security/ir.model.access.csv if you define any custom models
    ],
    'installable': True,
    'application': True,
}