# -*- coding: utf-8 -*-
from odoo import models, fields, api , _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    narration = fields.Html(related='move_id.narration')