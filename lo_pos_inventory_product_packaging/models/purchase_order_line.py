# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, float_round
import math


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def _prepare_sale_order_line_data(self, line, company):
        """ Generate the Sales Order Line values from the PO line
            :param line : the origin Purchase Order Line
            :rtype line : purchase.order.line record
            :param company : the company of the created SO
            :rtype company : res.company record
        """
        data = super(PurchaseOrder, self)._prepare_sale_order_line_data(line, company)
        data['product_packaging_qty'] = line.product_packaging_qty
        data['product_packaging_id'] = line.product_packaging_id.id if line.product_packaging_id else False
        return data


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    package_uom_id = fields.Many2one(
        'uom.uom',string='Package UoM',
        related="product_packaging_id.package_uom_id",
        store=True
    )
    exclude_in_package_qty = fields.Boolean(
        'Exclude In Package',default=False
    )

    # override base function for removing warning
    @api.onchange('product_packaging_id')
    def _onchange_product_packaging_id(self):
        pass

    # added new onchange on product_qty for automatically change product_qty according to product_packaging_qty
    @api.onchange('product_qty')
    def _onchange_product__qty(self):
        for line in self:
            # rounding the product_packaging_qty of line
            line.product_packaging_qty = float(math.ceil(line.product_packaging_qty))
            if line.product_packaging_id:
                packaging_uom = line.product_packaging_id.product_uom_id
                qty_per_packaging = line.product_packaging_id.qty
                product_qty = packaging_uom._compute_quantity(line.product_packaging_qty * qty_per_packaging, line.product_uom)
                if float_compare(product_qty, line.product_qty, precision_rounding=line.product_uom.rounding) != 0 and not line.exclude_in_package_qty:
                    line.product_qty = product_qty

    # override base function for rounding product_packaging_qty
    @api.depends('product_packaging_id', 'product_uom', 'product_qty')
    def _compute_product_packaging_qty(self):
        self.product_packaging_qty = 0
        for line in self:
            if not line.product_packaging_id:
                continue
            if line.exclude_in_package_qty:
                line.product_packaging_qty = float(math.floor(line.product_packaging_id._compute_qty(line.product_qty, line.product_uom))) if float(math.floor(line.product_packaging_id._compute_qty(line.product_qty, line.product_uom))) >= 1.00 else float(math.ceil(line.product_packaging_id._compute_qty(line.product_qty, line.product_uom)))
            else:
                line.product_packaging_qty = float(math.ceil(line.product_packaging_id._compute_qty(line.product_qty, line.product_uom)))

    # # override base function for rounding product_packaging_qty
    @api.depends('product_packaging_qty')
    def _compute_product_qty(self):
        for line in self:
            # rounding the product_packaging_qty of line
            line.product_packaging_qty = float(math.ceil(line.product_packaging_qty))
            if line.product_packaging_id:
                packaging_uom = line.product_packaging_id.product_uom_id
                qty_per_packaging = line.product_packaging_id.qty
                product_qty = packaging_uom._compute_quantity(line.product_packaging_qty * qty_per_packaging, line.product_uom)
                if float_compare(product_qty, line.product_qty, precision_rounding=line.product_uom.rounding) != 0 and not line.exclude_in_package_qty:
                    line.product_qty = product_qty

    # add condition for changes in select suggested_packaging instead of product_packaging_id of line
    @api.depends('product_id', 'product_qty', 'product_uom')
    def _compute_product_packaging_id(self):
        for line in self:
            # remove packaging if not match the product
            if line.product_packaging_id.product_id != line.product_id:
                line.product_packaging_id = False
            # suggest biggest suitable packaging matching the PO's company
            if line.product_id and line.product_qty and line.product_uom:
                suggested_packaging = line.product_id.packaging_ids \
                    .filtered(lambda p: p.purchase and (p.product_id.company_id <= p.company_id <= line.company_id)) \
                    ._find_suitable_product_packaging(line.product_qty, line.product_uom)
                line.product_packaging_id = suggested_packaging if suggested_packaging.id == line.product_packaging_id.id else line.product_packaging_id