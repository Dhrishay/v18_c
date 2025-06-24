# © 2020 OpenIndustry.it
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order for Request Product From DC",
    "version": "18.0.0.1",
    "license": "AGPL-3",
    "description": """
        ale Order for Request Product From DC
    """,
    "category": "Sale",
    "website": "laooddoo.com",
    "depends": [
        "base","sale","account","purchase_request","purchase",
        "sh_sale_dynamic_approval", "sh_purchase_dynamic_approval","lod_multi_scrap_adjust_code","sale_purchase", "purchase_stock", "account_inter_company_rules", "approvals"
    ],
    "data": [
        "data/cron.xml",
        "wizard/return_request_order_views.xml",
        "security/ir.model.access.csv",
        "security/group.xml",
        "views/purchase_order.xml",
        "views/picking.xml",
        "views/invoice_and_bill.xml",
        "views/res_company.xml",
        "views/sale_order_view.xml",
        "views/inherit_sale_order.xml",
        "views/res_config_views.xml",
        "views/res_partner_views.xml",
        "views/dc_menu.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'lod_request_product_to_dc/static/src/views/account_move_list_controller.js',
            'lod_request_product_to_dc/static/src/views/account_move_kanban_controller.js'
        ],
    },
    "images": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
