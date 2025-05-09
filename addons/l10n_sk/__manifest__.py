# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Slovak - Accounting',
    'icon': '/account/static/description/l10n.png',
    'countries': ['sk'],
    'version': '1.0',
    'author': '26HOUSE (http://www.26house.com)',
    'website': 'https://www.odoo.com/documentation/17.0/applications/finance/fiscal_localizations.html',
    'category': 'Accounting/Localizations/Account Charts',
    'description': """
Slovakia accounting chart and localization: Chart of Accounts 2020, basic VAT rates +
fiscal positions.

Tento modul definuje:
 Slovensk tov osnovu za rok 2020

 Zkladn sadzby pre DPH z predaja a nkupu

 Zkladn fiklne pozcie pre slovensk legislatvu


Pre viac informci kontaktujte info@26house.com alebo navtvte https://www.26house.com.

    """,
    'depends': [
        'base_iban',
        'base_vat',
        'account',
    ],
    'data': [
        'views/res_partner_views.xml',
        'views/res_company_views.xml',
        'views/report_invoice.xml',
        'views/account_move_views.xml',
        'views/report_template.xml',
    ],
    'demo': [
        'demo/demo_company.xml',
    ],
    'license': 'LGPL-3',
}
