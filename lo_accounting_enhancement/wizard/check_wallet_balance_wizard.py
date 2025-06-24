# -*- coding:utf-8 -*-
from odoo import fields, models, api, _

import base64
import qrcode
import io
import json
import hashlib
import random
import requests
from odoo.exceptions import UserError, RedirectWarning
from datetime import datetime, timedelta, date

class CheckBranchBalanceWizard(models.TransientModel):
    _name = "check.branch.balance.wizard"
    _description = "Check Branch balance Wizard"

    # login_token = fields.Char("Login Token")
    # login_date = fields.Datetime("Login Date")
    # date_exp = fields.Datetime("Login Date")
    
    def action_confirm(self):
        print('====Confirm Check Branch balance===>')
        return True
        # chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        # random_loginKey = ''.join(random.SystemRandom().choice(chars) for i in range(8))

        # config_param = self.env['ir.config_parameter'].sudo()

        # kok_kok_url = config_param.get_param('pos_kok_payment_cr.kok_kok_url')
        # member_id = config_param.get_param('pos_kok_payment_cr.member_id')
        # member_pass = config_param.get_param('pos_kok_payment_cr.member_pass')
        # member_wallet_account = config_param.get_param('pos_kok_payment_cr.member_wallet_account')

        # member_pass = hashlib.sha512(member_pass.encode('utf-8')).hexdigest()
        # member_pass = member_pass + random_loginKey
        # member_pass = hashlib.sha512(member_pass.encode('utf-8')).hexdigest()

        # login_url = kok_kok_url + "/member-api-service/v1.0.1/member/login"
        # headers = {'Content-Type': 'application/json'}
        # body = {
        #     "memberId": member_id,
        #     "memberPassword": member_pass,
        #     "loginKey": random_loginKey
        # }
        # response = requests.post(login_url, data=json.dumps(body), headers=headers)
  
        # login_data = response.json()
        # if login_data.get('respStatus') == 'SUCCESS':
        #     get_response = login_data.get('responseObj')
        #     token = get_response.get('memberToken')
        #     date = datetime.strptime(get_response.get('tokenGenTime'),"%Y%m%d%H%M%S")
        #     date = date.strftime("%Y-%m-%d %H:%M:%S")
            
            
        #     config_param.set_param('pos_kok_payment_cr.login_token', token)
        #     config_param.set_param('pos_kok_payment_cr.login_date', date)

        #     return {'type': 'ir.actions.act_window_close'}
        # else:
        #     raise UserError(_('You can not Generate Token'))

class CheckMainBalanceWizard(models.TransientModel):
    _name = "check.main.balance.wizard"
    _description = "Check Main balance Wizard"

    # login_token = fields.Char("Login Token")
    # login_date = fields.Datetime("Login Date")
    # date_exp = fields.Datetime("Login Date")
    
    def action_confirm(self):
        print('====Confirm Check Main balance===>')
        return True