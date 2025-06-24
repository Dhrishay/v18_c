# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    status = fields.Selection([
        ('new','New'),
        ('confirm','Confirm'),
        ('waste','Waste'),
        ('void','Void'),
        ('waste_and_void','Waste & void')]
    )

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ['status']
        return params