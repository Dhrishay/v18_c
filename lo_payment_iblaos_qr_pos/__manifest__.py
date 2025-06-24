# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

{
    'name': "Payment IBlaos QR POS",
    'description': """  """,
    'category': 'POS',
    'version': '18.0.0.1',
    'depends': ['point_of_sale'],
    'author': "laoodoo",
    'data': [
        'views/journal_view.xml',
        'views/res_config.xml',
        'views/pos_view.xml',
    ],
    'website': 'https://www.laoodoo.com',
    'assets': {
        'point_of_sale._assets_pos': [
            'lo_payment_iblaos_qr_pos/static/src/js/PaymentScreen.js',
            'lo_payment_iblaos_qr_pos/static/src/js/chrome.js',
            'lo_payment_iblaos_qr_pos/static/src/js/posstore.js',
            'lo_payment_iblaos_qr_pos/static/src/xml/PaymentScreen.xml',
        ],
        'point_of_sale.customer_display_assets': [
            'lo_payment_iblaos_qr_pos/static/src/xml/QrCode.xml'
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "LGPL-3",
}
