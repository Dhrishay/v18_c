# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Pos Pay Later',
    'summary': """Pos Pay Later""",
    'description': """Pos Pay Later""",
    'version': '18.0.0.0',
    'author': "laoodoo",
    'website': 'https://www.laoodoo.com',
    'license': 'LGPL-3',
    'depends': ['base', 'point_of_sale', 'pos_online_payment'],
    'data': [
        'views/pos_payment_method.xml',
        'views/pos_order_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'lo_pos_pay_later/static/src/js/payment_screen.js',
        ],
    },
}
