# -*- coding: utf-8 -*-

{
    'name': 'Access User Access Manager',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/user_profile_views.xml',
        'views/access_manager_views.xml',
        'views/ir_ui_button_views.xml',
        'views/ir_ui_notebook_page_views.xml',
        'data/ir_ui_button_data.xml',
        'data/ir_ui_notebook_page_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'access_users_manager/static/src/js/loading_indicator.js',
            # 'access_users_manager/static/src/js/form_arch_parser.js',
            'access_users_manager/static/src/js/form_controller.js',
            # 'access_users_manager/static/src/js/field.js',
        ],
    },
    "license": "LGPL-3",
    'application': True,
}
