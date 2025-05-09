# -*- coding: utf-8 -*-
{
    'name': "Employee Commission Management",
    'summary': "HR Employee Commission Tracking",
    'description': """
        This module allows you to:
        - Define employee types (Commission-Based, Commission + Salary, Salary-Only, PASE)
        - Track commission history and percentages
        - Monitor current and total commission earnings
        - PASE employees get special access and an accounting journal automatically created
    """,
    'author': "ziaurrehmanii",
    'website': "",
    'category': 'Human Resources/Employees',
    'version': '0.1',
    'depends': [
        'base', 
        'hr', 
        'hr_contract', 
        'hr_payroll', 
        'hr_payroll_account',
        'account',  # For journal creation
        'sale',     # For sales access
        'purchase', # For purchase access
    ],
    'data': [
        'security/security.xml',
        'views/employee_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}