# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import models, api


class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.model
    def _load_pos_data_models(self, config_id):
        data = super()._load_pos_data_models(config_id)
        data += ['void.reasons','pos.void.reason.history']
        return data

    def _loader_params_pos_order_line(self):
        result = super()._loader_params_pos_order_line()
        result['search_params']['fields'].append('barcode')
        return result
