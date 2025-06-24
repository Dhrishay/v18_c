# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    void_reasons_ids = fields.Many2many('void.reasons',string='Reasons')
    scrap_product = fields.Boolean(string='Scrap product')
    show_employee = fields.Boolean(string='Show Employee in Line')
    on_void = fields.Boolean(string='On Void')

