# -*- coding: utf-8 -*-
from odoo import _, api, Command, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        if self.group_id and self.group_id.sale_id and self.group_id.sale_id.request_type:
            vals['request_type'] = True
        if self.group_id and self.group_id.sale_id and self.group_id.sale_id.return_request_type:
            vals['return_request_type'] = True
            picking_type_id = self.env['stock.picking.type'].search([('id', '=', self.env['ir.config_parameter'].get_param(
                'lod_request_product_to_dc.operation_type'))])
            vals['picking_type_id'] = picking_type_id.id
        return vals