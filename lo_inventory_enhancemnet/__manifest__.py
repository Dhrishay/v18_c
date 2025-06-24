{
    'name': 'Inventory Enhancement',
    'summary': 'LO Inventory Enhancement',
    'version': '18.0.1.0.0',
    'category': 'Inventory',
    'sequence': 1,
    'author': 'laooddoo',
    'license': 'LGPL-3',
    'website': 'http://www.laooddoo.com',
    'description':"""LO INVENTORY ENHANCEMENT""",
    'depends': ['stock', 'stock_barcode', 'web_tour', 'web_mobile', 'product',
        'website_sale', 'purchase', 'point_of_sale', 'mrp_account','stock_landed_costs'
    ],
    'external_dependencies': {
        'python': ['check_digit_EAN13']
    },
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'wizard/update_categories_view.xml',
        # 'views/res_company_views.xml',
        'views/product.xml',
        'views/batch_update_price.xml',
        'views/product_batch_price_views.xml',
        'views/product_template_views.xml',
        'views/x_tmp_competitor_views.xml',
        'views/purchase_order_view.xml',
        'views/stock_views.xml',
        'wizard/import_wizard.xml',
        'reports/report_received_dc.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'lo_inventory_enhancemnet/static/src/**/*.xml',
        ],
    },
    'demo':[],
    'application': True,
    'installable':True,
    'auto_install': False, 
}
