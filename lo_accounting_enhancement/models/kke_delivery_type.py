# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class KkeDeliveryType(models.Model):
    _name = "kke.delivery.type"
    _description = "KKE delivery type"

    name = fields.Char('Delivery type', required=True)
    code = fields.Char('Delivery code', required=True)