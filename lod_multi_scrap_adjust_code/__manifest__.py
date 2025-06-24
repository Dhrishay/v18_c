{
    'name': 'Multi Scraps in Inventory',
    'version': '18.0.1.0.0',
    'sequence': 0,
    'category': 'Stock',
    'summary': 'Multi-scraps Product',
    'description': 'Multi-scraps Product, odoo15',
    'author': 'Bounpheng Khounluesa',
    'company': 'Kokkok M',
    'maintainer': 'Kokkok M',
    'images': ['static/description/banner.png'],
    'website': 'https://www.kokkokm.com',
    'depends': ['base', 'stock', 'point_of_sale', 'product', 'report_xlsx', 'lo_inventory_enhancemnet'],
    'data': [
        'security/ir.model.access.csv',
        'security/adjust_security.xml',

        'views/product_multiscrap_views.xml',
        'views/product_views.xml',
        # 'views/res_company.xml',
        'views/user_view.xml',

        'reports/report_scrap_adjust.xml',
        'reports/report_daily_adjust.xml',
        # 'reports/report.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
    

}
