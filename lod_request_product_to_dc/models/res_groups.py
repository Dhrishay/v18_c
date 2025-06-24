from odoo import models, fields


class ResGroups(models.Model):
    _inherit = "res.groups"

    is_receive = fields.Boolean(string="Receive Stock")
    is_pick = fields.Boolean(string="Pick Stock")
    is_put_away = fields.Boolean(string="Put Away Stock")
    is_delivery = fields.Boolean(string="Delivery Stock")