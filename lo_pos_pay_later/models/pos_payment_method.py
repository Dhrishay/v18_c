# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    is_pay_later = fields.Boolean('Pay Later')

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ['is_pay_later']
        return params


class PosOrders(models.Model):
    _inherit = 'pos.order'

    pay_later_order = fields.Boolean('Pay Later Order')

    def set_pay_later_order(self):
        try:
            for rec in self:
                rec.pay_later_order = True
                if rec.name == '/':
                    rec.name = rec._compute_order_name()
                if rec.pay_later_order and not rec.account_move:
                    move_vals = rec._prepare_invoice_vals()
                    move_id = rec._create_invoice(move_vals)
                    rec.write({'account_move': move_id.id})
                    move_id.sudo().with_company(self.company_id).with_context(skip_invoice_sync=True)._post()
        except:
            return False
        return True

    def write(self, vals):
        pay_later_order_list = []
        for order in self:
            if order.account_move and 'account_move' in vals:
                vals.pop('account_move')
            if order.account_move and order.pay_later_order and 'pay_later_order' in vals and vals.get('pay_later_order') == False:
                pay_later_order_list.append(order.id)
        res = super(PosOrders, self).write(vals)
        for order in self:
            if order.id in pay_later_order_list:
                order._apply_invoice_payments(order.session_id.state == 'closed')
                order.account_move.with_context(skip_invoice_sync=True)._generate_and_send()
        return res

    def action_pos_order_paid(self):
        res = super(PosOrders, self).action_pos_order_paid()
        for rec in self:
            if rec.account_move:
                rec.write({'state': 'invoiced'})
            else:
                rec.write({'state': 'paid'})
        return res
