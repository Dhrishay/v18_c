{
     "name": "Website Sale Order Time Restrictions",
     "version": "18.0.0.0",
     "license": "LGPL-3",
     'summary': 'Restrict website sale order creation/confirmation based on time and days',
     'description': """
          Adds configuration options in Website settings to define allowed time windows and days for order creation and confirmation.
          Prevents or warns users when orders are placed outside allowed times.
    """,
     'author': "Candidroot Solution Pvt. Ltd.",
     'website': "https://candidroot.com",
     "category": "Website",
     "depends": ["sale_management", 'website_sale'],
     "data": [
          "security/ir.model.access.csv",
          "views/order_day_rule_view.xml",
          "views/res_config_settings_view.xml",
          "views/sale_order_error.xml",
     ],
     'application': False,
     'installable': True,
}