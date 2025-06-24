# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_bom_data(self):
        """
            If a product has one or more Bills of Materials (BOMs), it will return the components of the BOM;
            otherwise, it will return False.
        """
        bom_id = self.env['mrp.bom'].search([
            ('product_id', '=', self.id),
            ('company_id', 'child_of', self.env.company.id)],
            order='id desc', limit=1
        )
        if bom_id:
            return [line.product_id.name for line in bom_id.bom_line_ids]
        return False

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        fields += ['sequence']
        return fields