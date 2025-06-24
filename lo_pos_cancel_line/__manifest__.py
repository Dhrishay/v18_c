# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

{
    'name': "POS Line Cancel",
    'description': """  """,
    'category': 'POS',
    'version': '18.0.0.0',
    'depends': ['point_of_sale'],
    'author': "laoodoo",
    'data': [
        'views/pos_view.xml'
    ],
    'website': 'https://www.laoodoo.com',
    'assets': {
        'point_of_sale._assets_pos': [
            'lo_pos_cancel_line/static/src/js/ordersummery.js',
            'lo_pos_cancel_line/static/src/js/posorder.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "LGPL-3",
}
