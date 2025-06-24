# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.order"

    def send_notification(self, order_id, uuid):
        self.env.user.sudo()._bus_send(
            "update_order_notification",
            {'data': {'order_id': order_id, 'uuid': uuid}}
        )

    def switch_screen(self, screen, order):
        self.env.user.sudo()._bus_send(
            "switch_screen", {'data': {'screen': screen, 'order': order}}
        )

    def action_pad_update(self):
        self.env.user.sudo()._bus_send(
            "action_pad_update", {'data':[]}
        )

    def send_kitchen(self,order_id):
        self.env.user.sudo()._bus_send(
            "send_kitchen", {'data':{'order_id':order_id}}
        )
