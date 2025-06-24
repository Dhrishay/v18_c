from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_procurement_values(self):
        price_unit = self.sale_line_id.price_unit
        res = super()._prepare_procurement_values()
        if price_unit:
            res['price_unit'] = price_unit
        return res