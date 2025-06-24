# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Lao GP - Accounting',
    'countries': ['la'],
    'version': '2.0',
    'category': 'Accounting/Localizations/Account Charts',
    'description': """
Chart of Accounts for Laos GP.
===============================

Thai accounting chart and localization.
    """,
    'author': 'Candidroot Solutions',
    'depends': [
        'account',
        'lo_account_accounting',
    ],
    'auto_install':False,
    'demo': [
        'demo/demo_company.xml',
    ],
    'license': 'LGPL-3',
}
