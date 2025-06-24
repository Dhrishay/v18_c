# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, float_round

class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    package_uom_id = fields.Many2one('uom.uom',string='Package UoM')
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    display_name = fields.Char(compute='_compute_display_name', string='display_name')
    package_product_id = fields.Many2one('product.product', string='Packge Product')
    
    @api.depends('name','qty')
    def _compute_display_name(self):
        for res in self:
            res.display_name = f"{res.name if res.name else '/'} {int(res.qty)}"

    @api.constrains('barcode')
    def _check_barcode_uniqueness(self):
        domain = [('barcode', 'in', [b for b in self.mapped('barcode') if b])]
        if self.env['product.product'].search_count(domain, limit=1) and self.product_id:
            match_product_id = self.env['product.product'].sudo().search(domain, limit=1)
            if self.package_product_id and self.package_product_id.id != match_product_id.id:
                raise ValidationError(_("A product already uses the barcode"))

    @api.model_create_multi
    def create(self, values):
        res = super(ProductPackaging, self).create(values)
        for rec in res:
            product_id = rec.product_id if rec.product_id else False
            if product_id:
                if not rec.package_product_id:
                    package_product_id = self.env['product.product'].sudo().create({
                        'name' : rec.name if rec.name else "",
                        'type' : 'consu',
                        'is_storable' : True,
                        'is_pack_product' : True,
                        'categ_id' : product_id.categ_id.id if product_id.categ_id else False,
                        'uom_id' : rec.package_uom_id.id if rec.package_uom_id else False
                    })
                    rec.package_product_id = package_product_id.id
                    if package_product_id and rec:
                        bom_id = self.env['mrp.bom'].sudo().create({
                            'product_tmpl_id' : package_product_id.product_tmpl_id.id,
                            'product_id' : package_product_id.id,
                            'product_qty': 1.0,
                            'product_uom_id' : rec.package_uom_id.id if rec.package_uom_id else False,
                            'type' : 'phantom',
                            'bom_line_ids': [
                                (0, 0,
                                    {
                                        'barcode' : product_id.barcode,
                                        'product_id': product_id.id,
                                        'product_qty': rec.qty if rec.qty else 1.00,
                                        'is_pack' : True ,
                                        'product_packaging_id': rec.id
                                    }
                                ),
                            ],
                        })
                        package_product_id.barcode  = rec.barcode if rec.barcode else '' 
                else:
                    package_product_id = rec.package_product_id
                    package_product_id.is_pack_product = True
                    if package_product_id:
                        rec.barcode = package_product_id.barcode
        return res
