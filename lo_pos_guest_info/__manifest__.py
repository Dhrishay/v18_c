# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Pos Guest Information',
    'summary': """Pos Guest Information""",
    'description': """Pos Guest Information""",
    'version': '18.0.0.0',
    'author': "laoodoo",
    'website': 'https://www.laoodoo.com',
    'license': 'LGPL-3',
    'depends': ['base', 'pos_restaurant'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/res_config_settings_views.xml',
        'views/pos_order_view.xml',
        'views/guest_detail.xml',
        'views/guest_detail_report_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'lo_pos_guest_info/static/src/js/pos_store.js',
            'lo_pos_guest_info/static/src/js/guest_detail_model.js',
            'lo_pos_guest_info/static/src/js/control_buttons.js',
            'lo_pos_guest_info/static/src/js/actionpad_widget.js',
            'lo_pos_guest_info/static/src/number_of_guest_popup/number_of_guest.js',
            'lo_pos_guest_info/static/src/number_of_guest_popup/guest_detail_popup.js',
            'lo_pos_guest_info/static/src/xml/control_buttons.xml',
        ],
    },
}
