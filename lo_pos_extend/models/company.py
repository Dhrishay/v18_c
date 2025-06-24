from odoo import api, models, registry, fields, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    delivery_time = fields.Integer(string="Delivery Time")
