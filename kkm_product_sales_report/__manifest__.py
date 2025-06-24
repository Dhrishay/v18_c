# -*- coding: utf-8 -*-
{
    'name': "kkm_product_sales_report",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'category': 'Point Of Sale',
    'version': '18.0.0.1',
    'author': "Laoodoo",
    'website': 'https://www.laoodoo.com/',
    'license': 'LGPL-3',
    'depends': ['base','point_of_sale', 'report_xlsx'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report/product_sales_report.xml',
        'views/product_sales_report.xml',
        'wizard/product_sales_report_wizard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ]
}
