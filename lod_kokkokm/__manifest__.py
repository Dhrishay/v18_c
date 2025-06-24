{
    'name': 'Customize KokkoM',
    'version': '18.0',
    'sequence': 0,
    'category': 'All',
    'website': 'https://www.laoodoo.com',
    'summary': '',
    'description': """Customize for KokkoM""",
    'depends': ['base', 'product', 'purchase', 'point_of_sale', 'website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/ib_trans_no_view.xml'
    ],

    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
