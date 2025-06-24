# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Customer Credit Limit | Customer Credit | Credit Management',
    'version': '18.0.1.2',
    'sequence': 1,
    'category': 'Sales',
    'description':
        """
        odoo Apps will check the Customer Credit Limit on Sale order and notify to the sales manager,
        
        Customer Credit Limit, Partner Credit Limit, Credit Limit, Sale limit, Customer Credit balance, Customer credit management, Sale credit approval , Sale customer credit approval, Sale Customer Credit Informatation, Credit approval, sale approval, credit workflow , customer credit workflow,
    Customer credit limit
    Customer credit limit warning
    Check customer credit limit
    Configure customer credit limit
    How can set the customer credit limit
    How can set the customer credit limit on odoo
    How can set the customer credit limit in odoo
    Use of customer credit limit on sale order
    Change customer credit limit
    Use of customer credit limit on customer invoice
    Customer credit limit usages
    Use of customer credit limit
    Set the customer credit limit in odoo
    Set the customer credit limit with odoo
    Set the customer credit limit
    Customer credit limit odoo module
    Customer credit limit odoo app
    Customer credit limit email
    Set credit limit for customers
    Warning message to customer on crossing credit Limit
    Auto-generated email to Administrator on cutomer crossing credit limit.
    Credit limit on customer
    Credit limit for customer
    Customer credit limit setup        

    """,
    'summary': 'Customer Credit Limit Partner Credit Limit Credit Limit Sale limit Customer Credit balance Customer credit management Sale credit approval Sale customer credit approval Sale Customer Credit Informatation',
    'depends': ['sale_management', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/customer_limit_wizard_view.xml',
        'views/partner_view.xml',
        'views/sale_order_view.xml',
    ],
	'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    #author and support Details
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':45.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
    'pre_init_hook' :'pre_init_check',
    "license": "LGPL-3",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
