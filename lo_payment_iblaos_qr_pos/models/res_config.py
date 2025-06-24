# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.


from odoo import fields, models, api, _
import json
import hashlib
import random
import requests
from odoo.exceptions import UserError, RedirectWarning
from datetime import datetime, timedelta, date


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    is_iblaos_payment = fields.Boolean("Is IBLoas Payment")
    is_prompt_pay = fields.Boolean('Is Prompt Payment')
    is_rabbit_linepay = fields.Boolean('Is Rabbit LinePay Payment')
    is_true_money = fields.Boolean('Is True Money Payment')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    iblaos_url = fields.Char("IBLoas Url")
    memberId = fields.Char("Member ID")
    memberPassword = fields.Char("Member Password ")
    callback_url = fields.Char("Call Back Url")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('lo_payment_iblaos_qr_pos.iblaos_url', self.iblaos_url)
        set_param('lo_payment_iblaos_qr_pos.memberId', self.memberId)
        set_param('lo_payment_iblaos_qr_pos.memberPassword', self.memberPassword)
        set_param('lo_payment_iblaos_qr_pos.callback_url', self.callback_url)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res['iblaos_url'] = get_param('lo_payment_iblaos_qr_pos.iblaos_url')
        res['memberId'] = get_param('lo_payment_iblaos_qr_pos.memberId')
        res['memberPassword'] = get_param('lo_payment_iblaos_qr_pos.memberPassword')
        res['callback_url'] = get_param('lo_payment_iblaos_qr_pos.callback_url')
        return res
