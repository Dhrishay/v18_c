{
    'name': 'LaOdoo Reward Program',
    'version': '18.0.1.0.0',
    'description': 'This module enhance the functionality of exising reward and promotions functionality.',
    'summary': 'This module enhance the functionality of exising reward and promotions functionality.',
    'author': 'Candidroot Solution Pvt. Ltd.',
    'license': 'LGPL-3',
    
    'depends': ['loyalty', 'sale', 'sale_loyalty', 'point_of_sale'],
    'data': [
        'views/loyalty_reward_views.xml',
        'views/pos_config_view.xml',
        'views/promotion.xml',
        'wizard/sale_loyalty_reward_wizard_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'lod_reward_program/static/src/js/control_button.js',
            'lod_reward_program/static/src/js/pos_store.js',
        ],
    },
    'auto_install': False,
    'application': False,
    
}