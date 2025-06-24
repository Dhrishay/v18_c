# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResUser(models.Model):
    _inherit = 'res.users'

    stock_location_ids =  fields.Many2many('stock.location', string="Allow Location")

    def data_clear(self):
        for rec in self:
            rec.stock_location_ids = [(5,0,0)]