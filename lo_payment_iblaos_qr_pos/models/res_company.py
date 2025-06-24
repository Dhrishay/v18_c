# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class res_company(models.Model):
    _inherit = "res.company"

    pc_code = fields.Char('Branch Code')
