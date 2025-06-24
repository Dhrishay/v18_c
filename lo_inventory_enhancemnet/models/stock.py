# -*- coding: utf-8 -*-

from odoo import fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_calculated = fields.Boolean(
        'Is Calculated', default=False
    )
    
    def button_validate(self):
        res = super(StockPicking , self).button_validate()
        for picking in self:
            if picking.picking_type_id.code == 'outgoing' and picking.sale_id:
                if picking.sale_id.invoice_status in ['to invoice', 'no']:
                    if not picking.sale_id.is_without_price:
                        picking.sale_id._create_invoices()
        return res
