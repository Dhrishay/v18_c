# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Laoodoo
# See LICENSE file for full copyright and licensing details.

{
    'name': "Pos Multi Currency Payment",
    'summary': 'User can do payment in multiple-currency on POS Screen',
    'description': """
        The User will get the option to pay in multiple-currency on the PaymentScreen.
        This payment in multi-currency will be reflected on receipt as well as backend.
    """,
    'category': 'Point Of Sale',
    'version': '18.0.0.0',
    'author': "Laoodoo",
    'website': 'https://www.laoodoo.com/',
    'license': 'LGPL-3',
    'depends': ['point_of_sale'],
    'data': [
        'views/res_config_settings.xml',
        'views/pos_order_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'lo_multi_currency_pos/static/src/js/pos_store.js',
            'lo_multi_currency_pos/static/src/js/Popups/MultiCurrencyPopup.js',
            'lo_multi_currency_pos/static/src/xml/MultiCurrencyPopup.xml',
            'lo_multi_currency_pos/static/src/js/PaymentScreen/payment_screen.js',
            'lo_multi_currency_pos/static/src/xml/OrderReciept.xml',
            'lo_multi_currency_pos/static/src/xml/PaymentScreen.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
