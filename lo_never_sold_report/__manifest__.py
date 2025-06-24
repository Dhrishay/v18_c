# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

{
    'name': "Never Sold Report",
    'description': """ Never Sold Report """,
    'category': 'Inventory',
    'version': '18.0.1.0.0',
    'depends': ['stock'],
    'author': "laoodoo",
    'data': [
        'security/ir.model.access.csv',
        'report/category_pdf_report.xml',
        'wizard/never_sold_wizard.xml',
    ],
    'website': 'https://www.laoodoo.com',
    'assets': {
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "LGPL-3",
}