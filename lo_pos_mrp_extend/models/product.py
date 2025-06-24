# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_takeaway = fields.Boolean('Takeaway',company_dependent=True)
    takeaway_bom_id = fields.Many2one('mrp.bom', 'Bill of Material',company_dependent=True)
