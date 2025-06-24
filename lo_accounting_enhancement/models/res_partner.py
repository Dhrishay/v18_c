# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class LODResPartner(models.Model):
    _inherit = 'res.partner'
    _description =  'Customer Extend'

    partner_code = fields.Char('Customers Code')
    fax = fields.Char(string='Fax')