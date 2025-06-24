# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    def action_genrate_sequence(self):
        for rec in self:
            if rec.division_code and rec.department_code:
                new_code = rec.division_code + rec.department_code
                div_sequence = self.env['ir.sequence'].sudo().search([('code', '=', new_code)])
                if not div_sequence:
                    self.env['ir.sequence'].sudo().create({
                        'name': new_code,
                        'code': new_code,
                        'prefix': new_code,
                        'padding': 5,
                        'company_id': False
                    })
            elif rec.division_code:
                division_code = rec.division_code
                div_sequence = self.env['ir.sequence'].sudo().search([('code','=',division_code)])
                if not div_sequence:
                    self.env['ir.sequence'].sudo().create({
                        'name': division_code,
                        'code': division_code,
                        'prefix': division_code,
                        'padding': 5,
                        'company_id': False
                    })
        return True

    def action_genrate_costing_method(self):
        for rec in self:
            rec.property_cost_method = 'average'
            rec.property_valuation = 'real_time'
