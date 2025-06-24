# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_name_la = fields.Char(
        string='Product Name(LA)',
        compute='_compute_product_name_la',
        store=True
    )
    product_owner = fields.Many2one('res.partner', string='Product Owner')

    def action_generate_item_code(self):
        for rec in self:
            default_code = ''
            if rec.categ_id and rec.categ_id.division_code and rec.categ_id.department_code:
                new_code = rec.categ_id.division_code + rec.categ_id.department_code
                default_code = self.env['ir.sequence'].next_by_code(new_code)
            elif rec.categ_id and rec.categ_id.division_code:
                default_code = self.env['ir.sequence'].next_by_code(rec.categ_id.division_code)
            if default_code:
                rec.default_code = default_code

    @api.depends('product_variant_id', 'name')
    def _compute_product_name_la(self):
        for record in self:
            if record.product_variant_id:
                # Set the lang context to 'lo_LA' for the related field
                product_name_la = record.product_variant_id.with_context(lang='lo_LA').name
                record.product_name_la = product_name_la
            else:
                record.product_name_la = False

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if 'categ_id' in val and val['categ_id']:
                categ_id = self.env['product.category'].sudo().search([('id','=',val['categ_id'])])
                if categ_id:
                    default_code = ''
                    if categ_id and categ_id.division_code and categ_id.department_code:
                        new_code = categ_id.division_code + categ_id.department_code
                        default_code = self.env['ir.sequence'].next_by_code(new_code)
                    elif categ_id and categ_id.division_code:
                        default_code = self.env['ir.sequence'].next_by_code(categ_id.division_code)
                    if default_code:
                        val['default_code'] = default_code
        return super().create(vals)
