# -*- coding: utf-8 -*-
{
    'name': "Branch Warehouse Automation",
    'summary': "Creates a new warehouse for each child company (branch)",
    'description': """
        This module automatically creates a new warehouse when a child company (branch) is created.
        It ensures that each branch company has its own warehouse for better inventory management and organization.
    """,
    'author': "ziaurrehmanii",
    'website': "",
    'category': 'Inventory/Inventory',
    'version': '0.1',
    'depends': ['base', 'stock'],
    'data': [
    'security/security.xml',
    'views/company_views.xml',
    'views/stock_warehouse_views.xml',
    'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}