# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    def get_action_picking_tree_ready_kanban(self):
        return self._get_action('stock_barcode.stock_picking_action_kanban')




