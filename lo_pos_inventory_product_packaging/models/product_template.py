# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, float_round
from odoo.tools import float_utils
from odoo.http import content_disposition, request

class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_pack_product = fields.Boolean(string='Pack Product', default=False)

    def print_pdf_report_of_stock(self):
        object_list = []
        if self:
            for rec in self:
                small_product_qty = rec.with_company(
                    self.env.user.company_id
                )._compute_quantities_dict()[rec.id]['qty_available']
                product_list = [
                    ('Product', rec.name),
                    (rec.uom_id.name, small_product_qty)
                ]
                packagings = self.env['product.packaging'].sudo().search([
                    ('product_id', 'in', rec.product_variant_ids.ids),
                    ('package_product_id', '!=', False)
                ])
                if packagings:
                    for package in packagings:
                        package_qty = package.package_product_id.with_company(
                            self.env.user.company_id
                        )._compute_quantities_dict(None,None,None)[package.package_product_id.id]['qty_available']
                        package_uom = ' (' + package.package_uom_id.name + ') ' if package and package.package_uom_id else False
                        product_list.append(
                            (package.package_product_id.name + package_uom if package_uom else '', package_qty)
                        )
                    object_list.append(product_list)

        if not object_list or not self:
            raise ValidationError(_("There are no Data Available For Selected Products."))
        data = {
            'docs': self,
            'object_list': object_list
        }
        return self.env.ref(
            'lo_pos_inventory_product_packaging.action_product_stock_report_product_template'
        ).report_action(self.ids, data=data)

class ProductProduct(models.Model):
    _inherit = "product.product"

    def _check_duplicated_packaging_barcodes(self, barcodes_within_company, company_id):
        packaging_domain = self._get_barcode_search_domain(barcodes_within_company, company_id)
        if self.env['product.packaging'].sudo().search_count(packaging_domain, limit=1):
            is_same_product = False
            match_packaging_id = self.env['product.packaging'].sudo().search(packaging_domain)
            if match_packaging_id and self.is_pack_product:
                bom_lines = self.env['mrp.bom.line'].sudo().search([
                    ('product_packaging_id.id', '=', match_packaging_id.id),
                    ('bom_id.type','=','phantom')
                ])
                for bom_line_id in bom_lines:
                    if bom_line_id.bom_id.product_id.id == self.id:
                        is_same_product = True
                        break
            if not is_same_product:
                raise ValidationError(_("A packaging already uses the barcode"))

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ['is_pack_product']
        return params

    @api.model
    def _get_fields_stock_barcode(self):
        fields = super()._get_fields_stock_barcode()
        fields.append('is_pack_product')
        fields.append('barcode_ids')
        return fields

    def _get_stock_barcode_specific_data(self):
        data = super()._get_stock_barcode_specific_data()
        data['product.barcode.multi'] = self.env['product.barcode.multi'].search([('company_id','in',[self.env.company.id])]).read(
            self.env['product.barcode.multi']._get_fields_stock_barcode(), load=False
        )
        return data

    def print_pdf_report_of_stock(self):
        object_list = []
        if self:
            for rec in self:
                small_product_qty = rec.with_company(
                    self.env.user.company_id
                )._compute_quantities_dict(None, None, None)[rec.id]['qty_available']
                product_list = [('Product' , rec.name),(rec.uom_id.name,small_product_qty)]

                packagings = self.env['product.packaging'].sudo().search([
                    ('product_id', '=', rec.id),
                    ('package_product_id', '!=', False)
                ])
                if packagings:
                    for package in packagings:
                        package_qty = package.package_product_id.with_company(
                            self.env.user.company_id
                        )._compute_quantities_dict(None, None, None)[package.package_product_id.id]['qty_available']
                        package_uom = ' (' + package.package_uom_id.name +') ' if package and package.package_uom_id else False
                        product_list.append(
                            (package.package_product_id.name +  package_uom if package_uom else '', package_qty)
                        )
                    object_list.append(product_list)

        if not object_list or not self:
            raise ValidationError(_("There are no Data Available For Selected Products."))
        data = {
            'docs': self,
            'object_list': object_list
        }
        return self.env.ref(
            'lo_pos_inventory_product_packaging.action_product_stock_report_product_product'
        ).report_action(self.ids, data=data)

