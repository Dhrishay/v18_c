# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

{
    'name': "POS Void ",
    'description': """  """,
    'category': 'POS',
    'version': '18.0.0.0',
    'depends': ['point_of_sale','lo_pos_cancel_line','pos_hr','lo_multi_user_login'],
    'author': "laoodoo",
    'data': [
        'security/ir.model.access.csv',
        'wizard/product_wizard.xml',
        'views/voip_reason.xml',
        'views/pos_view.xml',
        'views/pos_void_reason_history.xml',
        'views/pos_order.xml',
        'views/scrap_form_view.xml',
    ],
    'website': 'https://www.laoodoo.com',
    'assets': {
        'point_of_sale._assets_pos': [
            'lo_pos_void/static/src/js/controll_button.js',
            'lo_pos_void/static/src/js/void_reason.js',
            'lo_pos_void/static/src/js/PosStore.js',
            'lo_pos_void/static/src/js/OrderLine.js',
            'lo_pos_void/static/src/js/void_list_popup.js',
            'lo_pos_void/static/src/xml/control_button.xml',
            'lo_pos_void/static/src/xml/voipcontrollbutton.xml',
            'lo_pos_void/static/src/xml/OrderLine.xml',
            'lo_pos_void/static/src/xml/voidreasonlistpopup.xml'
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "LGPL-3",
}
