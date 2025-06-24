from odoo import tools
from odoo import fields, models, api


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    asset_type = fields.Selection([
        ('sale', 'Sale: Revenue Recognition'),
        ('purchase', 'Purchase: Asset'),
        ('expense', 'Deferred Expense')
    ], compute='_compute_asset_type', store=True, index=True)

    @api.depends('original_move_line_ids')
    def _compute_asset_type(self):
        for record in self:
            if not record.asset_type and record.original_move_line_ids:
                account = record.original_move_line_ids.account_id
                if account.account_type == 'liability_current' or account.account_type == 'liability_non_current':
                    record.asset_type = 'sale'
                elif account.account_type == 'asset_current' or account.account_type == 'asset_prepayments':
                    record.asset_type = 'expense'
                elif account.account_type == 'asset_fixed' or account.account_type == 'asset_non_current':
                    record.asset_type = 'purchase'    
                else:
                    record.asset_type = False