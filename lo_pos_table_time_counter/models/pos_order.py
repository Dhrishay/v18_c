# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    start_time = fields.Datetime('Start Time')
    end_time = fields.Datetime('End Time')
    duration = fields.Float('Duration')


class PosConfig(models.Model):
    _inherit = 'pos.config'

    table_timer_enable = fields.Boolean()


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_table_timer_enable = fields.Boolean(
        related='pos_config_id.table_timer_enable', readonly=False
    )
