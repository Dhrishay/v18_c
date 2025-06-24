# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.


{
    'name': "Account Accounting",
    'description': """
    """,
    'category': 'POS',
    'version': '18.0.0.0.0',
    'depends': ['account', 'account_asset', 'account_reports', 'account_budget'],
    'data': [
        'data/balance_sheet.xml',
        'data/profit_loss.xml',
        'views/account_view.xml'
    ],
    'author': "Laoodoo",
    'website': 'https://www.laoodoo.com',
    "license": "LGPL-3",
    'installable': True,
    'application': True,
    'auto_install': False,
}
