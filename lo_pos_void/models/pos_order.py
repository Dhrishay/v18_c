# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.order"

    void_ids = fields.One2many('pos.void.reason.history','pos_order_id',string='Void Line')
    scrap_ids = fields.One2many('stock.scrap','order_id',string='Scrap Line')



class StockScrap(models.Model):
    _inherit = "stock.scrap"

    order_id = fields.Many2one('pos.order','Pos Order')
    extra_note = fields.Text('Extra Note')
