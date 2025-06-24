# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import ast

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression

class LoyaltyRule(models.Model):
    _inherit = 'loyalty.rule'

    name = fields.Char(string="Name", compute="_compute_rule_name")

    def _compute_rule_name(self):
        for rec in self:
            rec.name = ''
            if rec.program_id and (rec.program_id and rec.minimum_qty):
                rec.name = f"{rec.minimum_qty} Quantity Rule"