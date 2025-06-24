# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_barcode = fields.Char(
        'Product Barcode', related='product_id.barcode',
        store=True
    )