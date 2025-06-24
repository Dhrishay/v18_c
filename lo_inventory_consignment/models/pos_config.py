from odoo import api, fields, models, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    mto_purchase_order = fields.Boolean('Create Purchase Order')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mto_purchase_order = fields.Boolean(
        related='pos_config_id.mto_purchase_order',
        readonly=False
    )
