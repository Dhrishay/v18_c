from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    asset_id = fields.Many2one('account.asset')
    is_created_from_asset = fields.Boolean()
