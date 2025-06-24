# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import base64
import io
import json
import hashlib
import random
import requests


class IBTransaction(models.Model):
    _name = 'lod.ib.transaction'
    _description = 'Get Transaction ID'

    name = fields.Char('Transaction No')
    date = fields.Datetime('Date')
    receive_order_no = fields.Char('Receive Order No')
    amount = fields.Float('Amount')
    phone = fields.Char('Phone')
    # branch_id = fields.Many2one('res.branch', string='Branch')
    # pos_id = fields.Many2one('pos.config', string='POS')
    branch_id = fields.Char('Branch')
    pos_id = fields.Char('POS')
    src_bank = fields.Char('Source Bank')
    channel = fields.Char('Channel')
    dest_bank = fields.Char('Destination Bank')
    payment_status = fields.Char('Payment Status')