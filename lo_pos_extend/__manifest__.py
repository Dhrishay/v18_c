# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Pos Extend',
    'summary': """Pos Extend""",
    'description': """Pos Extend""",
    'version': '18.0.0.0',
    'author': "laoodoo",
    'website': 'https://www.laoodoo.com',
    'license': 'LGPL-3',
    'depends': ['base', 'pos_restaurant'],
    'assets': {
        'point_of_sale._assets_pos': [
            'lo_pos_extend/static/src/js/pos_store.js',
            'lo_pos_extend/static/src/xml/ticket_screen.xml',
            'lo_pos_extend/static/src/xml/ReceiptHeader.xml',
        ],
    },
}
