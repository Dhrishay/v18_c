# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.


{
    'name': "Custom Reward",
    'description': """
    """,
    'category': 'POS',
    'version': '18.0.0.0.0',
    'depends': ['point_of_sale', 'pos_loyalty', 'sale_loyalty'],
    'data': [
        'views/res_config_settings_views.xml',
        'security/ir.model.access.csv'
    ],
    'author': "Laoodoo",
    'website': 'https://www.laoodoo.com',
    'assets': {
        'point_of_sale._assets_pos': [
            # 'lo_custom_reward/static/src/js/bus.js',
            'lo_custom_reward/static/src/js/pos_order.js',
            'lo_custom_reward/static/src/js/control_buttons.js',
            'lo_custom_reward/static/src/js/selection_popup.js',
            'lo_custom_reward/static/src/js/ticket_screen.js',
        ],
        'point_of_sale.customer_display_assets': [
            'lo_custom_reward/static/src/xml/CustomerFacingDisplayOrder.xml',
        ],
    },
    "license": "LGPL-3",
    'installable': True,
    'application': True,
    'auto_install': False,
}
