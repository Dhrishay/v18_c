# -*- coding: utf-8 -*-
#################################################################################
# Author      : laoodoo. ()
# Copyright(c): 2015-Present laoodoo.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
    "name": "Automatic Company Configuration",
    "summary": """The module automatically set configuration.""",
    "category": "Extra Tools",
    "version": "1.0.1",
    "author": "laoodoo",
    'website': 'https://www.laoodoo.com',
    "description": """""",
    "depends": [
        'base', 
        'analytic', 
        'account', 
        'account_inter_company_rules',
        'account_budget',
        'contacts',
        'sh_pos_analytic_tags',
        'point_of_sale',
        'accountant',
        'sale_purchase_inter_company_rules', 
        'stock', 
        'lo_account_accounting',
        'sale_margin',
        'loyalty',
        'product',
        'sale', 
        'purchase',
        'website_sale',
        'purchase_requisition',
        'stock_dropshipping',
        'mrp',
        'quality_control',
        'mrp_workorder',
        'base_vat',
        'stock_accountant',
        'account_reports',
        'sh_account_dynamic_approval',
        'sh_purchase_dynamic_approval'
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/analytic_plan_view.xml',
        'views/res_district_view.xml',
        'views/sale_zone_ordering.xml',
        'views/res_company_view.xml',
        'wizard/analytic_wizard_create_company.xml',
        'wizard/analytic_wizard_create_sub_company.xml',
    ],
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "price": 0,
    "currency": "USD",
    "license": "LGPL-3",
    "pre_init_hook": "set_fields_configration",
}
