# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.


from odoo import fields, models, api, _


class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_iblaoqr = fields.Boolean('Is IB LaoQR')
    wallet_ib_name = fields.Char('Wallet Name')
    wallet_ib_account = fields.Char('IB Account No')
    wallet_ib_merchant_id = fields.Char('Merchant ID')
    icon_qr = fields.Image("QR Icon", max_width=128, max_height=128)
