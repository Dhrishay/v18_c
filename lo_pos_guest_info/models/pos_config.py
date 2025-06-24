# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    is_guest_details = fields.Boolean()
    guest_details_timing = fields.Selection([
        ('before', 'Order Before'),
        ('after', 'Order After')
    ], string="Guest Details Timing")
    guest_details_required = fields.Boolean()


class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.model
    def _load_pos_data_models(self, config_id):
        data = super()._load_pos_data_models(config_id)
        data += ['guest.detail']
        return data


class PosOrders(models.Model):
    _inherit = 'pos.order'

    guest_detail_ids = fields.One2many(
        'guest.detail', 'order_id', string='Guest Details'
    )
    no_of_male = fields.Integer('Male')
    no_of_female = fields.Integer('Female')

    def write(self, values):
        res = super(PosOrders, self).write(values)
        guest_orders = self.filtered(
            lambda x: x.config_id and x.config_id.is_guest_details
        )
        for order in guest_orders:
            guest_detail_list = []
            remaining_male = order.no_of_male - len(order.guest_detail_ids.filtered(
                lambda x: x.gender == 'male')
            )
            remaining_female = order.no_of_female - len(order.guest_detail_ids.filtered(
                lambda x: x.gender == 'female')
            )
            if order.state in ('paid', 'invoiced'):
                for male in range(0, abs(remaining_male)):
                    guest_detail_list += [(0, 0, {
                        'gender': 'male',
                        'config_id': order.config_id.id if order.config_id else False,
                        'company_id': order.company_id.id if order.company_id else False,
                        'session_id': order.session_id.id if order.session_id else False,
                        'country_id': order.company_id.country_id.id if order.company_id.country_id else False,
                        'user_id': order.user_id.id if order.user_id else False
                    })]
                for female in range(0, abs(remaining_female)):
                    guest_detail_list += [(0, 0, {
                        'gender': 'female',
                        'config_id': order.config_id.id if order.config_id else False,
                        'company_id': order.company_id.id if order.company_id else False,
                        'session_id': order.session_id.id if order.session_id else False,
                        'country_id': order.company_id.country_id.id if order.company_id.country_id else False,
                        'user_id': order.user_id.id if order.user_id else False
                    })]
            if guest_detail_list:
                order.guest_detail_ids = guest_detail_list
        return res
