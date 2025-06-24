# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    kke_url = fields.Char("KKE URL",config_parameter="lod_api_kke.kke_url")
    kke_api_key = fields.Char("KKE API Key",config_parameter="lod_api_kke.kke_api_key")