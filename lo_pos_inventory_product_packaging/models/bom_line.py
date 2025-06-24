# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, float_round

class BomLine(models.Model):
    _inherit = "mrp.bom.line"

    product_packaging_id = fields.Many2one(
        'product.packaging', 'Packaging',
        domain="[('product_id', '=', product_id)]"
    )
    is_pack = fields.Boolean(string='Pack',default=False)

    @api.onchange('product_id','product_qty')
    def onchange_product_qty(self):
        if self.product_id and self.product_qty > 0.00:
            applyable_package_ids = [
                package for package in self.product_id.packaging_ids if package.qty == self.product_qty
            ]
            if applyable_package_ids:
                applyable_package = min(applyable_package_ids, key=lambda r: r.sequence)
                self.is_pack = True
                self.product_packaging_id = applyable_package.id
            else:
                self.is_pack = False
                self.product_packaging_id = False