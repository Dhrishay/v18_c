from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    asset_id = fields.Many2one('account.asset')
