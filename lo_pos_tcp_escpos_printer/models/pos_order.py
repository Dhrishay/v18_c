# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    sticker_note = fields.Char(string="Sticker Note")

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        fields += ['sticker_note']
        return fields
