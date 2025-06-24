from . import models
from . import wizard


def set_configrations_fields(env):
    env['res.config.settings'].sudo().create({
        'group_uom': True, 
        'group_stock_packaging': True, 
        'group_discount_per_so_line': True, 
        'group_product_pricelist': True, 
        'module_purchase_requisition': True, 
        'module_stock_dropshipping': True,  
        'group_cash_rounding': True,
        'group_analytic_accounting': True,
        'module_account_budget': True,
    }).execute()

def _module_uninstall(env):
    install_modules = env['ir.module.module'].search([('name', 'in', ['account_batch_payment','account_check_printing', 'account_bank_statement_import_csv'])])
    if install_modules:
        for module in install_modules:
            if module.state == 'installed':
                module.sudo().button_uninstall()

def set_language_lao(env):
    lao_lang = env['res.lang'].sudo().search([('code','=', 'lo_LA'), ('active', '=', False)])
    lao_lang.active = True

def set_fields_configration(env):
    set_configrations_fields(env)
    _module_uninstall(env)
    set_language_lao(env)



#  env['res.config.settings'].sudo().create({
#     'group_uom': True, 
#     'group_stock_packaging': True, 
#     'group_discount_per_so_line': True, 
#     'group_product_pricelist': True, 
#     # 'module_loyalty': True, 
#     # 'module_sale_margin': True, 
#     # 'group_sale_order_template': False, 
#     # 'portal_confirmation_pay': False, 
#     # 'group_delivery_invoice_address': True, 
#     # 'default_invoice_policy': 'delivery', 
#     'module_purchase_requisition': True, 
#     'module_stock_dropshipping': True, 
#     # 'group_mrp_routings': False, 
#     # 'module_quality_control': True, 
#     # 'group_mrp_wo_tablet_timer': False, 
#     # 'vat_check_vies': True, 
#     'group_cash_rounding': True,
#     'group_analytic_accounting': True,
#     'module_account_budget': True,
#     # 'totals_below_sections': True,
# }).execute()