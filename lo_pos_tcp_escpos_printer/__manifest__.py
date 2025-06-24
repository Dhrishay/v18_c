# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Laoodoo
# See LICENSE file for full copyright and licensing details.

{
    'name': 'POS TCP ESC/POS Printer',
    'category': 'Sales/Point of Sale',
    'version': '18.0.0.0',
    'author': "Laoodoo",
    'website': 'http://laooddoo.com/',
    'license': 'LGPL-3',
    'sequence': 10,
    'summary': 'POS TCP ESC/POS Printers in PoS',
    'description': """
        Use POS TCP ESC/POS Printers without the IoT Box in the Point of Sale
        If you use Python3.10 then you need to install pip3 install python-escpos escpos==2.0
    """,
    'depends': ['point_of_sale', 'pos_restaurant'],
    'external_dependencies': {"python": ["escpos"]},
    'data': [
        'security/mutli_company_security.xml',
        'security/ir.model.access.csv',
        'views/pos_config_views.xml',
        'views/res_config_settings_views.xml',
        'views/pos_printer_views.xml',
        'views/receipt_design_custom_view.xml',
        'views/pos_note_view.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'lo_pos_tcp_escpos_printer/static/src/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
}
