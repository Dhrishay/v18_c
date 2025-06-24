# -*- coding: utf-8 -*-
#################################################################################
# Author : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

{
    'name': 'Top Sale Report',
    'version': '18.0.1.0.0',
    'summary': 'Top Sale Report',
    'description': """ 
    """,
    'category': 'General',
    'author': ' ',
    'website': '',
    'price': 35.00, 
    'license': 'AGPL-3',
    'depends': ['base', 'point_of_sale','report_xlsx'], 
    'data': [
        'security/ir.model.access.csv',
        # 'report/report.xml', 
        'wizard/top_sale_wizard.xml', 
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
