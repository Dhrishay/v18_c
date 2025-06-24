# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        lot = self.env['stock.lot'].search([
            ('product_id', '=', self.product_id.id)
        ], limit=1)
        vals = super()._prepare_move_line_vals(quantity, reserved_quant)
        if self._context.get('active_model') == 'account.asset':
            vals.update({'lot_id': lot.id})
        return vals
