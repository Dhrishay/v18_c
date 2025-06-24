
{
    'name': 'Stock Adjustment Report',
    'version': '18.0.1.0.0',
    'description': '',
    'summary': 'Report for Stock Adjustment',
    'author': '',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'stock','lod_multi_scrap_adjust_code',
    ],
    'data': [
        'security/ir.model.access.csv',

        'wizard/stock_adjustment_report_wiz_view.xml',
        
        'reports/stock_adjustment_xlsx_report_template.xml',
        'reports/stock_adjustment_report_template.xml',
    ],
    'auto_install': False,
    'application': False,
}





# lo_stock_adjustment_report