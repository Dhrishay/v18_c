# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.


{
    'name': "Asset Location",
    'description': """
    """,
    'category': 'Accounting',
    'version': '18.0.0.0.0',
    'depends': ['account', 'account_asset', 'stock', 'lo_account_accounting','sh_sale_dynamic_approval', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/asset_view.xml',
        'views/stock_picking_view.xml',
        'views/account_move_views.xml',
        'wizard/serial_number_wizard.xml',
        'wizard/asset_change_location_wizard.xml',
        'wizard/asset_serial_number.xml',
        'wizard/asset_modify_views.xml',
        'views/menu.xml',
    ],
    'author': "Laoodoo",
    'website': 'https://www.laoodoo.com',
    "license": "LGPL-3",
    'installable': True,
    'application': True,
    'auto_install': False,
}
