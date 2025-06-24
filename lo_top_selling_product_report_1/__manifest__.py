{
    'name': 'Top Selling Product Report',
    'version': '18.0.0.1',
    'summary': 'Top Selling Product Report',
    'description': """
        Top Selling Product Report
    """,
    'license': 'AGPL-3',
    'depends': ['base', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/top_selling_wizard_view.xml',
        'report/top_selling_products_pdf_report.xml',

    ],
    'installable': True,
    'auto_install': False,
}
# -*- coding: utf-8 -*-

