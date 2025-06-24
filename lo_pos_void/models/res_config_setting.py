# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_void_reasons_ids = fields.Many2many(
        related='pos_config_id.void_reasons_ids', string='Reasons', readonly=False
    )
    pos_scrap_product = fields.Boolean(related='pos_config_id.scrap_product')
    pos_show_employee = fields.Boolean(related='pos_config_id.show_employee')
    pos_on_void = fields.Boolean(related='pos_config_id.on_void')
