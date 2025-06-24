# -*- coding: utf-8 -*-
from odoo import api,fields, models


class Product(models.Model):
    _inherit = "product.product"


    product_trade_term = fields.Selection(
        related="product_tmpl_id.product_trade_term",
        string='Type',
        readonly=True,
    )
