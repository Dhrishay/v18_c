{
    'name' : "Inventory Transfer Report",
    'version' : "18.0.0.1",
    'category' : "Extra Tools",
    'author': 'Candidroot Solutions Pvt. Ltd.',
    'website': 'https://www.candidroot.com',
    'summary': 'Inventory Transfer Report',
    'description' : '''
             Inventory Transfer Report. 
    ''',
    'depends' : ['base', 'stock','lod_request_product_to_dc','report_pdf_options'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/inventory_transfer_report.xml',
        'report/inventory_trasfer_report_view.xml',
        'report/inventory_trasfer_report_action.xml',
             ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license':'LGPL-3'
}
