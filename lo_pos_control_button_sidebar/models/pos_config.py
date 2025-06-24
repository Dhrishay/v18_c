# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class POSConfig(models.Model):
    _inherit = 'pos.config'

    ## Make collapsible sidebar when enable is_control_button_side_bar on pos screen
    is_control_button_side_bar = fields.Boolean(string="Action on the left side")
