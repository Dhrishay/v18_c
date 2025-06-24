# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

{
    'name': "Multi Session login user",
    'description': """  """,
    'category': 'POS',
    'version': '18.0.0.0',
    'depends': ['point_of_sale'],
    'author': "laoodoo",
    'data': [
    ],
    'website': 'https://www.laoodoo.com',
    'assets': {
        'point_of_sale._assets_pos': [
            'lo_multi_user_login/static/src/js/**/*',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "LGPL-3",
}
