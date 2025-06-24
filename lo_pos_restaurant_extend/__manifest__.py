# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Pos Restaurant Extend',
    'summary': """Pos Pos Restaurant Extend""",
    'description': """Pos Restaurant Extend""",
    'version': '18.0.0.0',
    'author': "laoodoo",
    'website': 'https://www.laoodoo.com',
    'license': 'LGPL-3',
    'depends': ['base', 'point_of_sale','pos_restaurant', 'pos_preparation_display', 'mrp','product'],
    'data': [
            'views/product_view.xml',
    ],
    'assets': {
        'pos_preparation_display.assets': [
            'lo_pos_restaurant_extend/static/src/xml/kitchen_screen.xml',
            'lo_pos_restaurant_extend/static/src/js/orderline.js'
        ],
        'point_of_sale._assets_pos': [
            'lo_pos_restaurant_extend/static/src/js/product_screen.js'
        ],
    },
}
