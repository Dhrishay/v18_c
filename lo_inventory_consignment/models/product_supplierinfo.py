# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    trade_term = fields.Selection(
        related="partner_id.trade_term",
        readonly=True
    )

    @api.onchange('partner_id')
    def _onchage_vendor_price(self):
        for rec in self:
            if rec.partner_id:
                product_id = self.env['product.template'].search([('id', '=', int(rec._context.get('default_product_tmpl_id')))])
                price = (rec.partner_id.gp_compensation_per / 100) * product_id.list_price
                final_price = product_id.list_price - price
                rec.price = final_price if final_price > 0 else 0.0
