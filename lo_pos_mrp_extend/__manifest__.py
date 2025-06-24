# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'MRP Extend',
    'summary': """MRP Extend""",
    'description': """MRP Extend""",
    'version': '18.0.0.0',
    'author': "laoodoo",
    'website': 'https://www.laoodoo.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mrp', 'product', 'point_of_sale', 'pos_restaurant'],
    'data': [
        'views/product_view.xml',
    ],
}
