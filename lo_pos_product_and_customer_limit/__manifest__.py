# -*- coding: utf-8 -*-
{
    'name': "Pos Product and Customer Limit",
    'summary': "",
    'description': """""",
    'author': "",
    'website': "",
    'category': 'Sales/Point Of Sale',
    'version': '18.0.0.1',
    'depends': ['base','point_of_sale'],
    'data': [
        'views/pos_config_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            "lo_pos_product_and_customer_limit/static/src/js/data_service.js"
        ]
    },
}