# -*- coding: utf-8 -*-
{
    'name': "POS Customer Limit and Customer Loading",
    'summary': "Adds limited customer loading with optional background loading in POS.",
    'description': """
        This module introduces two key features for the Point of Sale system:
        - Limited Partners Loading: Allows you to control the number of partners (customers) shown in the POS.
        - Number of Customers Loaded: Displays the total number of customers loaded, based on the limit defined.
    """,
    'author': "Candidroot Solution Pvt. Ltd.",
    'website': "https://candidroot.com",
    'license': 'LGPL-3',
    'category': 'Sales/Point Of Sale',
    'version': '18.0.0.0',
    'depends': ['base','point_of_sale'],
    'data': [
        'views/pos_config_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'los_pos_partner_limit/static/src/js/load_partners.js'
        ]
    },
    'installable': True,
    'application': False,
}