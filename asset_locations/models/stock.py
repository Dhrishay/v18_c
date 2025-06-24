# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    asset_id = fields.Many2one('account.asset')
    is_asset_tranfer = fields.Boolean('Asset Tranfer')
    asset_count = fields.Integer(compute="_compute_asset_id")
    
    @api.depends('asset_id')
    def _compute_asset_id(self):
        for rec in self:
            asset_id = rec._get_asset_ids()
            rec.asset_count = len(asset_id)

    def _get_asset_ids(self):
        assets = self.env["account.asset"].search(
            [('picking_ids', 'in', self.id)]
        )
        return assets.ids


    def action_view_asset(self):
        action = {
            "name": _("Assets"),
            "res_model": "account.asset",
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "domain": [("id", "in", self._get_asset_ids())],
        }
        return action


