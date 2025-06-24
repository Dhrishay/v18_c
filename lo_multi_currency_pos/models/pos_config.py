# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Laoodoo
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    multi_currency_payment = fields.Boolean(
        'Multi Currency', help='To enable multi currency payment in pos'
    )
    payment_currency_ids = fields.Many2many(
        'res.currency', string="Currencies"
    )
