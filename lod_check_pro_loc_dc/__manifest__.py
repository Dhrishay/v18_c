{
    'name' : 'Check Detail for Product and Location',
    'version' : '0.0',
    'sequence': 1,
    'category': 'All',
    'website' : 'https://www.laoodoo.com',
    'summary' : '',
    'description' : """""",
    'depends': [
        'stock','stock_barcode', 'stock_picking_batch', 'website',
        'lo_inventory_enhancemnet','lo_purchase_enhancement','product_multiple_barcodes'
    ],
    'data': [        
        'security/security.xml',
        'data/data.xml',
        'view/page_menu.xml',
        'view/res_user.xml',
        'view/stock_picking_batch.xml',
        'view/check_location_template.xml',
        'view/check_product_template.xml',
        'view/product_template.xml',
        'view/check_stock_location_free_view.xml',
        'view/header_footer_view.xml', 
        ],
    'assets': {
        'web.assets_backend': [
            'lod_check_pro_loc_dc/static/src/components/barcode_pda.xml',
            'lod_check_pro_loc_dc/static/src/components/search_barcode_location_and_product.xml',
            'lod_check_pro_loc_dc/static/src/components/search_barcode_location_and_product.js',
            # 'lod_check_pro_loc_dc/static/src/components/button_check_loction.js',
        ],
        'web.assets_frontend': [
            'lod_check_pro_loc_dc/static/src/scss/check_price.scss',
            'lod_check_pro_loc_dc/static/src/scss/header.scss',
            'lod_check_pro_loc_dc/static/src/scss/kokkok.scss',
            'lod_check_pro_loc_dc/static/src/scss/navbar.scss',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}