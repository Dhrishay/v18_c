# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('la')
    def _get_la_template_data(self):
        return {
            'property_account_income_categ_id': 'l10_la_4100011_1',
            'property_account_expense_categ_id': 'l10_la_5100011_1',
            'property_stock_valuation_account_id': 'l10_la_1300011_1',
            'property_stock_account_input_categ_id': 'l10_la_1300012_1',
            'property_stock_account_output_categ_id': 'l10_la_1300013_1',
            'property_stock_account_production_account_id': 'l10_la_5100011_1',
            'property_account_receivable_id': 'l10_la_1200111',
            'property_account_payable_id': 'l10_la_2400011',
            'property_stock_valuation_account_id': 'l10_la_8100111',
        }

    @template('la', 'res.company')
    def _get_la_res_company(self):
        return {
            self.env.company.id: {
                'account_fiscal_country_id': 'base.la',
                'bank_account_code_prefix': '1400',
                'cash_account_code_prefix': '1100',
                'transfer_account_code_prefix': '17',
                # 'account_default_pos_receivable_account_id': 'la_gp_recv_pos',
                # 'income_currency_exchange_account_id': 'la_income_gain',
                # 'expense_currency_exchange_account_id': 'la_exp_loss',
                # 'account_sale_tax_id': 'tax_output_vat',
                # 'account_purchase_tax_id': 'tax_input_vat',
            },
        }
