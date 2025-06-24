# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_control_button_side_bar = fields.Boolean(
        related="pos_config_id.is_control_button_side_bar", readonly=False
    )

