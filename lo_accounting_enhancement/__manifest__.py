# -*- coding: utf-8 -*-

{
    'name': 'Accounting Enhancement',
    "version": "18.0.0.1",
    'category': 'Accounting/Accounting',
    'website': '',
    'author': '',
    'license': 'Other proprietary',
    'depends': ['base','account', 'sale', 'lo_account_accounting', 'lo_inventory_enhancemnet', 'lod_multi_scrap_adjust_code'],
    "description": "",
    'data': [
        'security/ir.model.access.csv',
        'security/master_franchise_security.xml',
        'views/account_move.xml',
        'views/sale_order.xml',
        'views/currency_rate_view.xml',
        'reports/report.xml',
        'reports/account/report_invoice_taladlao.xml',
        'reports/account/report_invoice_account_taladlao.xml',
        'reports/account/report_cash_payment_request_report_taladlao.xml',
        'reports/account/report_bank_payment_request_report_taladlao.xml',
        'reports/account/report_cash_receipt.xml',
        'reports/account/report_bank_receipt.xml',
        'reports/account/invoice_master_franchise.xml',
        'reports/account/report_receipt.xml',
        'reports/account/jmart_invoice.xml',

        'reports/account/report_cash_receipt_report.xml',
        'reports/account/report_bank_receipt_report.xml',
        'reports/account/report_cash_payment_request_taladlao.xml',
        'reports/account/report_bank_payment_request_taladlao.xml',
        'wizard/check_wallet_balance_wizard_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
        	'lo_accounting_enhancement/static/src/css/custom.css',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
