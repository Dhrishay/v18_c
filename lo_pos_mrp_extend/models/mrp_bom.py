# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, models
from odoo.tools import frozendict


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    # override base method for specific bom pickings
    @api.model
    def _bom_find(self, products, picking_type=None, company_id=False, bom_type=False):
        """ Find the first BoM for each products

        :param products: `product.product` recordset
        :return: One bom (or empty recordset `mrp.bom` if none find) by product (`product.product` record)
        :rtype: defaultdict(`lambda: self.env['mrp.bom']`)
        """
        bom_by_product = defaultdict(lambda: self.env['mrp.bom'])
        products = products.filtered(lambda p: p.type != 'service')
        if not products:
            return bom_by_product
        domain = self.sudo()._bom_find_domain(products, picking_type=picking_type, company_id=company_id, bom_type=bom_type)

        # Performance optimization, allow usage of limit and avoid the for loop `bom.product_tmpl_id.product_variant_ids`
        if len(products) == 1:
            bom = self.sudo().search(domain, order='sequence, product_id, id', limit=1)
            if bom:
                bom_by_product[products] = bom
            if products.with_company(self.env.company).is_takeaway and products.with_company(self.env.company).takeaway_bom_id and self.env.context.get('pos_order_type'):
                bom_by_product[products] = products.with_company(self.env.company).takeaway_bom_id
            return bom_by_product

        boms = self.sudo().search(domain, order='sequence, product_id, id')

        products_ids = set(products.ids)
        for bom in boms:
            products_implies = bom.product_id or bom.product_tmpl_id.product_variant_ids
            for product in products_implies:
                if product.id in products_ids and product not in bom_by_product:
                    bom_by_product[product] = bom

        return bom_by_product


class PosCOrders(models.Model):
    _inherit = 'pos.order'

    @api.model_create_multi
    def create(self, vals_list):
        res = super(PosCOrders, self).create(vals_list)
        for order in res:
            previous_context = dict(order.env.context)
            previous_context['pos_order_type'] = order.takeaway
            order.env.context = frozendict(previous_context)
        return res

    def write(self, vals_list):
        res = super(PosCOrders, self).write(vals_list)
        for order in self:
            previous_context = dict(order.env.context)
            previous_context['pos_order_type'] = order.takeaway
            order.env.context = frozendict(previous_context)
        return res
