# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class VoipReason(models.Model):
    _name = "void.reasons"
    _description = "Void Reasons"
    _inherit = ['pos.load.mixin']

    name = fields.Char('Reason')

    @api.model
    def _load_pos_data_domain(self, data):
        reason = [('id', 'in', data['pos.config']['data'][0]['void_reasons_ids'])] if data['pos.config']['data'][0][
            'void_reasons_ids'] else []
        return reason

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['name']
