# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Pos Table Time Counter',
    'summary': """Pos Table Time Counter""",
    'description': """Pos Table Time Counter""",
    'version': '18.0.0.0',
    'author': "laoodoo",
    'website': 'https://www.laoodoo.com',
    'license': 'LGPL-3',
    'depends': ['base', 'pos_restaurant', 'pos_preparation_display'],
    'data': [
        'views/pos_order_view.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'lo_pos_table_time_counter/static/src/js/payment_screen.js',
            'lo_pos_table_time_counter/static/src/js/actionpad_widget.js',
            'lo_pos_table_time_counter/static/src/js/floor_screen.js',
            'lo_pos_table_time_counter/static/src/xml/floor_screen.xml'
        ],
    },
}
