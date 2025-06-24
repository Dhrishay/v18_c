from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
     _inherit = 'res.config.settings'

     limited_partner_count = fields.Integer(string="Number of Customers Loaded", related="pos_config_id.limited_partner_count", readonly=False)
     partner_load_background = fields.Boolean(related="pos_config_id.partner_load_background", readonly=False)
     limited_partners_loading = fields.Boolean(string="Limited Customers Loading", related="pos_config_id.limited_partners_loading", readonly=False)

