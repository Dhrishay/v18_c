# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

import json
from odoo import fields, models, api, _
import base64
import qrcode
import io
import requests
from datetime import datetime, timezone


class LODPosOrderRewardResult(models.Model):
    _name = "lod.pos.order.reward.result"
    _description = "POS Reward Result"

    bill_id = fields.Integer(string="Bill ID")
    member_id = fields.Integer(string="Member ID")
    used_point = fields.Integer(string="Used Point")
    used_amount = fields.Integer(string="Used Amount")
    result = fields.Char(string="Result")
    reason = fields.Char(string="Reason")
    reward_type = fields.Selection([
        ('point', 'Point'),
        ('wallet', 'Wallet')],
        default='point', string="Reward Type")

class PosConfig(models.Model):
    _inherit = 'pos.config'

    loyalty_id = fields.Many2one('loyalty.program')
    use_incoming_points = fields.Boolean('Use incoming earning points')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_loyalty_id = fields.Many2one(
        'loyalty.program', related='pos_config_id.loyalty_id',
        readonly=False, domain="[('program_type', '=', 'loyalty')]"
    )
    pos_use_incoming_points = fields.Boolean(
        'Use incoming earning points', related='pos_config_id.use_incoming_points',
        readonly=False
    )


class PosOrder(models.Model):
    _inherit = "pos.order"
    url = 'https://member.kokkoksole.com/api/v1/third-party/odoo/push-notification'
    headers = {'Content-Type': 'application/json'}

    inv_name = fields.Char("INV Ref")

    @api.model
    def get_qr_code(self, data):
        data = json.dumps(data)
        img = qrcode.make(data)
        result = io.BytesIO()
        img.save(result, format='PNG')
        return base64.b64encode(result.getvalue()).decode()

    def refund_loyalty_points(self, points):
        if self.partner_id:
            domain = [
                ('partner_id', '=', self.partner_id.id),
                ('company_id', '=', self.env.company.id),
                ('program_id.active', '=', True),
                ('program_id.program_type', 'in', ['loyalty'])
            ]

            loyalty_card = self.env['loyalty.card'].search(domain, limit=1)
            if loyalty_card:
                loyalty_card.history_ids = [(0, 0, {
                    'description': 'Refund Points for ' + self.display_name,
                    'order_id': self.id,
                    'order_model': self._name,
                    'issued': points,
                    'card_id': loyalty_card.id
                })]
                loyalty_card.points += points

class LoyaltyProgram(models.Model):
    _inherit = 'loyalty.program'

    date_from = fields.Datetime(
        string="Start Date",
        help="The start date is included in the validity period of this program",
    )
    date_to = fields.Datetime(
        string="End date",
        help="The end date is included in the validity period of this program",
    )

    def _load_pos_data(self, data):
        res = super()._load_pos_data(data)
        loyalty_data = res.get('data')
        for item in loyalty_data:
            for key in ['date_from', 'date_to']:
                value = item.get(key)
                if isinstance(value, datetime):
                    value_uz = fields.Datetime.context_timestamp(self, value)  
                    item[key] = value_uz.isoformat()
                elif value is False:
                    item[key] = None 
        
        return res
        

class LoyaltyHistory(models.Model):
    _inherit = 'loyalty.history'
    url = 'https://member.kokkoksole.com/api/v1/third-party/odoo/push-notification'
    headers = {'Content-Type': 'application/json'}

    @api.model_create_multi
    def create(self, vals):
        loyalty_ids = super(LoyaltyHistory, self).create(vals)
        for loyalty in loyalty_ids:
            if loyalty.order_model == 'pos.order' and loyalty.order_id and loyalty.card_id.partner_id:
                partner_id = loyalty.card_id.partner_id
                title = 'ໄດ້ຮັບຄະແນນ'
                body = 'ທ່ານໄດ້ຮັບຄະແນນຈາກການຊື້ສິນຄ້າຈຳນວນ ' + "{:,.0f}".format(loyalty.issued) + ' ຄະແນນ'
                vals = {
                    "phone": partner_id.phone,
                    "title": title,
                    "body": body,
                }
                datas = json.dumps(vals)

                requests.request("POST", self.url, data=datas, headers=self.headers)
                self.env['res.partner.notice'].sudo().create({
                    'partner_id': partner_id.id,
                    'name': title,
                    'date': datetime.now(),
                    'body': body
                })
        return loyalty_ids


class ResPartnerNotice(models.Model):
    _name = 'res.partner.notice'
    _description = "Partner Notice"

    partner_id = fields.Many2one('res.partner', string='Customer')
    phone = fields.Char(related='partner_id.phone', string='Phone', store=True)
    date = fields.Datetime('Date')
    name = fields.Char('Title', translate=True)
    body = fields.Text('Body')