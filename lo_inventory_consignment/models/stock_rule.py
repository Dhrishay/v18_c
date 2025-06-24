from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.addons.stock.models.stock_rule import ProcurementException
from odoo.tools import groupby


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _update_purchase_order_line(self, product_id, product_qty, product_uom, company_id, values, line):
        res = super(StockRule, self)._update_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, line
        )
        partner = values['supplier'].partner_id
        if partner.trade_term == 'consignment' and values.get('price_unit', 0.0):
            price = (partner.gp_compensation_per / 100) * values.get('price_unit')
            price_unit = values.get('price_unit') - price
            res.update({"price_unit": price_unit})
        return res
