# -*- coding: utf-8 -*-
{
    'name': 'POS Control Buttons Style',
    'author': 'laoodoo',
    'version': '18.0.1.0',
    'website': 'https://www.laoodoo.com',
    'summary': "Add color,size for POS Control buttons",
    'description': """This functionality allows for the customization of Point of Sale (POS) control buttons by enabling the configuration of their size and color. 
    The button height and width can be adjusted to match specific design requirements or 
    screen layouts, while the background color of each button can be uniquely set based on 
    predefined options. These features provide businesses with a more visually appealing and 
    user-friendly interface, ensuring that the POS interface aligns with their branding and 
    operational needs. The customization is dynamically applied based on the configuration, 
    enhancing flexibility and usability
	""",
    "license": "LGPL-3",
    'depends': ['base', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/control_button_height_color.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'lo_pos_control_button_style/static/src/xml/control_button.xml',
            'lo_pos_control_button_style/static/src/js/product_screen.js',

        ],
    },
    'installable': True,
    'auto_install': False,
    'category': 'Point of Sale',
}
