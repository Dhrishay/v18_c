# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.
{
    'name': "POS Inventory Product Packaging",
    'summary': "",
    'description': "",
    'author': "Laoodoo",
    'website': 'https://www.laoodoo.com/',
    'category': 'Point Of Sale',
    'version': '18.0.0.1',
    'depends': ['base','product','stock','mrp','point_of_sale','stock_barcode','product_multiple_barcodes','sale','sale_purchase_inter_company_rules'],
    'data': [
        'views/mrp_bom.xml',
        'views/product_view.xml',
        'views/purchase_order_line.xml',
        'views/sale_order_view.xml',
        'views/packaging.xml',
        'report/picking_operations_report.xml',
        'report/product_packaging_report.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'lo_pos_inventory_product_packaging/static/src/js/pos_order_line.js',
        ],
        'web.assets_backend': [
            'lo_pos_inventory_product_packaging/static/src/js/barcode_object.js',
            'lo_pos_inventory_product_packaging/static/src/js/barcode_model.js',
            'lo_pos_inventory_product_packaging/static/src/js/lazy_barcode_cache.js',
        ],
    },
    "license": "LGPL-3",
}


