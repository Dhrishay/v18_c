
from odoo import tools
from odoo import fields, models, api


class AccountAccount(models.Model):
    _inherit = "account.account"

    account_type = fields.Selection(
        selection_add=[
            ("asset_receivable", "Trade and other receivables, net"),
            ("asset_receivable_related_party", "Receivable from related parties"),
            ("asset_cash", "Cash and cash equivalents"),
            ("asset_current", "Other current assets"),
            ("asset_non_current", "Other non-current assets"),
            ("asset_prepayments", "Prepayments"),
            ("asset_fixed", "Fixed Assets"),
            ("asset_inventory", "Inventories"),
            ('asset_property_equipment', "Property and equipment,net"),
            ("liability_payable", "Trade and other payables"),
            ('liability_borrowings',"Borrowings"),
            ("liability_credit_card", "Credit Card"),
            ("liability_current", "Other current liabilities"),
            ("liability_non_current", "Other Non-current Liabilities"),
            ('equity_share_capital',"Share capital"),
            ("equity", "Equity"),
            ("equity_unaffected", "Current Year Earnings"),
            ('equity_retain_earn',"Retained Earning"),
            ("income", "Revenue"),
            ("income_other", "Other Income"),
            ("expense", "Expenses"),
            ("expense_depreciation", "Depreciation Expenses"),
            ("expense_direct_cost", "Cost of Sales"),
            ('expense_admin',"Administrative Expenses"),
            ('expense_market',"Marketing Expenses"),
            ('expense_sell_commission',"Selling Commission"),
            ('expense_staff',"Staff Expenses"),
            ('expense_business_trip',"Business Trip Expenses"),
            ('expense_utility',"Utilities Expenses"),
            ('expense_rental',"Rental"),
            ('expense_income_tax',"Income tax expense"),
            ('expense_finance_cost',"Finance costs"),
            ("off_balance", "Off-Balance Sheet"),    
        ],
        string="Type",
        ondelete={
            "asset_receivable": "cascade",
            "asset_receivable_related_party": "cascade",
            "asset_cash": "cascade",
            "asset_current": "cascade",
            "asset_non_current": "cascade",
            "asset_prepayments": "cascade",
            "asset_fixed": "cascade",
            "asset_inventory": "cascade",
            "asset_property_equipment": "cascade",
            "liability_payable": "cascade",
            "liability_borrowings": "cascade",
            "liability_credit_card": "cascade",
            "liability_current": "cascade",
            "liability_non_current": "cascade",
            "equity_share_capital": "cascade",
            "equity": "cascade",
            "equity_unaffected": "cascade",
            "equity_retain_earn": "cascade",
            "income": "cascade",
            "income_other": "cascade",
            "expense": "cascade",
            "expense_depreciation": "cascade",
            "expense_direct_cost": "cascade",
            "expense_admin": "cascade",
            "expense_market": "cascade",
            "expense_sell_commission": "cascade",
            "expense_staff": "cascade",
            "expense_business_trip": "cascade",
            "expense_utility": "cascade",
            "expense_rental": "cascade",
            "expense_income_tax": "cascade",
            "expense_finance_cost": "cascade",
            "off_balance": "cascade",
        },
        default="asset_receivable",
    )
