# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_product_return = fields.Boolean('Is Product Return')

    @api.onchange('default_code')
    def _onchange_default_code(self):
        return


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_product_return = fields.Boolean(related='product_tmpl_id.is_product_return', string='Is Product Return', store=True)

    @api.onchange('default_code')
    def _onchange_default_code(self):
        return