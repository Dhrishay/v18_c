# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    is_auto_apply_reward = fields.Boolean(string="Auto Apply Promotions & Reward", default=False)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    is_auto_apply_reward = fields.Boolean(string="Auto Apply Promotions & Reward",related='pos_config_id.is_auto_apply_reward', readonly=False)