# -*- coding: utf-8 -*-
{
    'name': 'POS Control Buttons Sidebar',
    'author': 'laoodoo',
    'version': '18.0.1.0',
    'summary': "POS Control Buttons Sidebar",
    'description': """This module provides a configuration option to display all control buttons within a collapsible sidebar, 
    enhancing the Point of Sale interface. 
    Users can toggle the visibility of the control sidebar using a custom button, 
    allowing for a cleaner and more organized layout. When enabled, the sidebar 
    replaces the traditional placement of control buttons, offering a centralized and 
    space-efficient solution. 
    This feature is particularly useful for businesses that prefer a minimalistic or 
    streamlined interface while maintaining full functionality.
	""",
    'website': 'https://www.laoodoo.com',
    "license": "LGPL-3",
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/res_config_setting.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            # 'lo_pos_control_button_sidebar/static/src/xml/product_screen.xml',
            'lo_pos_control_button_sidebar/static/src/css/sidebar.css',
            'lo_pos_control_button_sidebar/static/src/js/product_screen.js',
            'lo_pos_control_button_sidebar/static/src/js/sidebar_service.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'category': 'Point of Sale',
}
