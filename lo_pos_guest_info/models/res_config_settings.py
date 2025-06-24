# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_is_guest_details = fields.Boolean(
        related='pos_config_id.is_guest_details', readonly=False
    )
    pos_guest_details_timing = fields.Selection(
        related='pos_config_id.guest_details_timing', readonly=False
    )
    pos_guest_details_required = fields.Boolean(
        related='pos_config_id.guest_details_required', readonly=False
    )

    @api.onchange('pos_is_guest_details')
    def onchange_pos_is_guest_details(self):
        if self.pos_is_guest_details and not self.pos_guest_details_timing:
            self.pos_guest_details_timing = 'before'
