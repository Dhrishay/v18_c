{
    "name": "Sale Order Custom",
    "version": "18.0.0.2",
    "license": "AGPL-3",
    "website": "",
    "category": "Sale",
    "depends": ["sale_management", 'account_accountant', 'stock_enterprise'],
    "data": [
        'data/server_actions.xml',
        'data/invoice_sequence.xml',
        'views/account.xml',
        'views/product.xml',
        'views/sale_order.xml',
        'views/report_invoice.xml',
        
        'report/account_move_export_invoice_report.xml',
        'report/account_move_local_invoice_report.xml'
    ],
    'assets': {
        'web.assets_common': [
            'sale_order_custom/static/src/img/topflight.jpeg',
        ],
    },

    'license':'LGPL-3',
    "application": True,
    "installable": True,
}