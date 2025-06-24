# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, float_round
import math

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _prepare_purchase_order_line_data(self, so_line, date_order, company):
        """ Generate purchase order line values, from the SO line
            :param so_line : origin SO line
            :rtype so_line : sale.order.line record
            :param date_order : the date of the orgin SO
            :param company : the company in which the PO line will be created
            :rtype company : res.company record
        """

        data = super(SaleOrder, self)._prepare_purchase_order_line_data(so_line, date_order, company)
        data['product_packaging_qty'] = so_line.product_packaging_qty
        data['product_packaging_id'] = so_line.product_packaging_id.id if so_line.product_packaging_id else False
        return data


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # override base function for removing warning
    @api.onchange('product_packaging_id')
    def _onchange_product_packaging_id(self):
        pass