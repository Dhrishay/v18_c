from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    operation_type = fields.Many2one('stock.picking.type', string='Operation Types', config_parameter='lod_request_product_to_dc.operation_type')