# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class PosNote(models.Model):
    _inherit = 'pos.note'

    kitechen_note = fields.Boolean('kitechen_note', copy=False)
    sticker_note = fields.Boolean('Sticker Note')

    @api.model
    def _load_pos_data_fields(self, config_id):
        return super()._load_pos_data_fields(config_id) + ['kitechen_note', 'sticker_note']
