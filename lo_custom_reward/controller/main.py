# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.bus.controllers.main import BusController
from odoo.addons.point_of_sale.controllers.main import PosController
import json
import requests
from datetime import datetime, timedelta


class Bus(BusController):
    def _poll(self, dbname, channels, last, options):
        channels = list(channels)
        if request.session.uid:
            user_id = request.env.ref('base.user_admin')
            channels.append(user_id)
        return super(Bus, self)._poll(dbname, channels, last, options)


class QrDict(PosController):
    url = 'https://member.kokkoksole.com/api/v1/third-party/odoo/push-notification'
    headers = {'Content-Type': 'application/json'}

    def _check_data(self, data):
        if not data.get('current_order'):
            return {
                "status": False,
                "message": "Please, Check current_order",
            }
        elif not data.get('session_id'):
            return {
                "status": False,
                "message": "Please, Check session_id",
            }
        elif not data.get('loyalty_point'):
            return {
                "status": False,
                "message": "Please, Check loyalty_point",
            }
        else:
            return {
                "status": True,
                "message": "Success",
            }

    @http.route(['/get/qr/point'], csrf=False, type='json', methods=['POST'], auth='public')
    def create_lead_acres(self, **kw):
        user_id = request.env.ref('base.user_admin').sudo()
        data = json.loads(request.httprequest.data)
        status = self._check_data(data)
        if status.get('status') == True:
            val = {
                'name': data.get('current_order'),
                'session_id': data.get('session_id'),
                'loyalty_point': data.get('loyalty_point')
            }
            user_id._bus_send("loyalty.point", {'type': val, 'user_id': user_id})

            partner_id = request.env['res.partner'].sudo().browse(data.get('member_id'))
            title = 'ຊຳລະສິນຄ້າດ້ວຍຄະແນນ'
            body = 'ທ່ານໄດ້ຊຳລະສິນຄ້າດ້ວຍຄະແນນຈຳນວນ ' + str(float((data.get('loyalty_point')))) + ' ຄະແນນ'
            vals = {
                "phone": partner_id.phone,
                "title": title,
                "body": body,
            }
            datas = json.dumps(vals)

            requests.request("POST", self.url, data=datas, headers=self.headers)

            request.env['res.partner.notice'].sudo().create({
                'partner_id': partner_id.id,
                'name': 'title',
                'date': datetime.now(),
                'body': body
            })

            res = {
                "success": True,
                "message": "Success",
                "responseCode": 1
            }
        else:
            res = {
                "success": False,
                "message": status.get('message'),
                "responseCode": 0
            }
        return res
