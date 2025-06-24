# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.http import Controller, Response, request, route
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
import requests
from datetime import datetime
import json

class SaleOrderInote(models.Model):
    _inherit = "sale.order"

    # ------------------------ add new 19/08/2024
    kke_total_cost = fields.Float(string="Total Cost", compute='_compute_kke_total_cost')
    kke_delivery_type_id = fields.Many2one('kke.delivery.type',string='Delivery Type')

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrderInote, self)._prepare_invoice()
        invoice_vals['sale_order_id'] = self.id
        return invoice_vals

    def action_confirm(self):
        res = super(SaleOrderInote, self).action_confirm()
        for record in self:
            if not record.kke_delivery_type_id:
                raise ValidationError(_('Please Select Delivery Type'))
        return res
     
    # -------------------# add new 19/08/2024-----------------
    @api.depends('order_line.product_uom_qty', 'order_line.product_id')
    def _compute_kke_total_cost(self):
        for order in self:
            kke_total_cost = sum(line.product_uom_qty * line.product_id.standard_price for line in order.order_line)
            order.kke_total_cost = kke_total_cost