{
    'name' : 'Backorder Configuration',
    'version' : '18.0.0.1',
    'sequence': 0,
    'category': 'Backorder Configuration',
    'website' : 'https://www.laooddoo.com/',
    'summary' : '',
    'description' : """Backorder Configuration""",
    'depends': ['stock', 'stock_barcode', 'mrp', 'point_of_sale','lo_product_markdown'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'view/sale_order_view.xml',
        'views/res_config_setting.xml',
        'views/stock_picking_type_view.xml',
        ],
    'assets': {
        'web.assets_backend': [
            
            'lod_backorder_config/static/src/js/barcode_model.js',
            'lod_backorder_config/static/src/js/barcode_picking_model.js',
            'lod_backorder_config/static/src/js/backorder_location_autocomplete.js',
            'lod_backorder_config/static/src/js/backorder_dialog.js',
            'lod_backorder_config/static/src/xml/backorder_dialog.xml',
        ],
       
    },
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}