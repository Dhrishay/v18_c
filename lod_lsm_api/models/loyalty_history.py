# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class LoyaltyHistory(models.Model):
    _inherit = 'loyalty.history'

    partner_id = fields.Many2one(related="card_id.partner_id", string="Customer", store=True)
