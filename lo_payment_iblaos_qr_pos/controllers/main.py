# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class IbLaosController(http.Controller):

    @http.route(['/iblaos/qr/callback'], type='json', auth='public', methods=['POST'],
                csrf=False)
    def iblaos_qr_callback(self, **kw):
        data = json.loads(request.httprequest.data)
        _logger.info("===========data===========%s", data)

        try:
            if data.get('message') == "success":
                if data.get("terminalLabel"):
                    # sendmany_busbus(data.get("terminalLabel"), data.get("txnAmount"))
                    self.sendmany_busbus(data.get("terminalLabel"), (data.get("txnRefId")))
                return {"status": "success"}
            else:
                _logger.warning("++++++ IB LaoQR ++++++ %s", e)
                return {"status": "failed"}

        except Exception as e:
            _logger.warning("++++++ IB QR Error ++++++ %s", e)
            return {"status": "failed"}

    def sendmany_busbus(self, terminal, pay_ref):
        user_id = request.env.ref('base.user_admin')
        terminal_split = terminal.split("|")
        if len(terminal_split) > 1:
            notification_data = {
                "order_name": terminal_split[1],
                "session_name": terminal_split[0],
                "pay_ref": pay_ref,
                # "amount": amount,
            }
            _logger.info("--------notification_data---------%s", notification_data)
            request.env['bus.bus'].sudo()._sendone(user_id.sudo().partner_id, 'iblaos_qr_callback', {'data': notification_data})
