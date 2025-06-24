# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.


from odoo import fields, models, api, _
from PIL import Image
import base64
import qrcode
import io
import json
from odoo.tools import file_open
import requests
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import random
import string
import logging
from odoo.tools.misc import file_open
from odoo.tools.image import image_data_uri, base64_to_image

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    def get_kok_ib_qr_code(self, order, amount, config_id, session_id):
        memberPassword = self.env['ir.config_parameter'].sudo().get_param('lo_payment_iblaos_qr_pos.memberPassword')
        iblaos_url = self.env['ir.config_parameter'].sudo().get_param('lo_payment_iblaos_qr_pos.iblaos_url')
        callback_url = self.env['ir.config_parameter'].sudo().get_param('lo_payment_iblaos_qr_pos.callback_url')
        member_id = self.env['ir.config_parameter'].sudo().get_param('lo_payment_iblaos_qr_pos.memberId')

        session_id = self.env['pos.session'].browse(int(session_id))
        config_id = self.env['pos.config'].browse(int(config_id))

        merchant_id = config_id.ib_journal_id.wallet_ib_merchant_id
        # Login generate token
        login_url = iblaos_url + "/IBInterBankServices/member/login"
        headers = {'Content-Type': 'application/json'}
        body = {
            "memberId": member_id,
            "memberPassword": memberPassword,
        }
        response = requests.post(login_url, data=json.dumps(body), headers=headers)

        login_data = response.json()
        if login_data.get('REASON') == 'Success':
            token = login_data.get('loginToken')

            qr_data = {
                "memberId": member_id,
                # "txnAmount": float_round(amount, 2),
                "txnAmount": "{:.2f}".format(amount),
                "purposeOfTxn": "Paid by IBLaos",
                "billNumber": str(order) + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)),
                "merchantId": merchant_id,
                "storeLabel": config_id.company_id and config_id.company_id.name or '',
                "terminalLabel": session_id.name + "|" + str(order),
                "memberDateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace("-", "").replace(":", "").replace(" ", ""),
                "callbackUrl": callback_url + "/iblaos/qr/callback",
            }
            _logger.info("=====IB=QR=DATA=======%s",qr_data)
            response = requests.post(iblaos_url + "/IBInterBankServices/member/bill/qr/generate",
                                     data=json.dumps(qr_data),
                                     headers={'Content-Type': 'application/json', 'AUTH_TOKEN': token})
            data = response.json()
            _logger.info('DATA Response>>>>>>>>>>>>>>>>>%s', data)
            if data.get('REASON') == 'Success':
                # Generate the QR Code
                qr_string = data.get("qrInformation", {}).get('qrString', '')
                if not qr_string:
                    raise ValueError("QR string is missing")

                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_H,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_string)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

                icon_bytes = config_id.ib_journal_id.icon_qr
                if icon_bytes:
                    icon_image = base64_to_image(icon_bytes)
                else:
                    icon_image = Image.open(file_open('lo_payment_iblaos_qr_pos/static/src/img/laoQR.png', mode='rb'))

                logo_size = 150
                logo = icon_image.resize(
                    (logo_size, int(logo_size * icon_image.size[1] / icon_image.size[0])), Image.LANCZOS
                )

                pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
                img.paste(logo, pos, mask=logo if logo.mode == 'RGBA' else None)
                result = io.BytesIO()
                img.save(result, format='PNG')
                return base64.b64encode(result.getvalue()).decode()
        else:
            raise UserError(_('You can not Generate Token'))


class PosConfig(models.Model):
    _inherit = "pos.config"

    ib_journal_id = fields.Many2one('account.journal', string='IB LaoQR Journal')
