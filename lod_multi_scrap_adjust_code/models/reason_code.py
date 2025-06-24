# Copyright (C) 2019 IBM Corp.
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ScrapReasonCode(models.Model):
    _name = "scrap.reason.code"
    _description = "Reason Code"

    name = fields.Char("Name")
    code = fields.Char("Code")
    description = fields.Text()
    location_id = fields.Many2one(
        "stock.location",
        string="Scrap Location",
    )
    received_loss = fields.Selection([
        ('received', 'Received'),
        ('loss', 'Loss'),
    ], default='loss', string='Received/Loss')
    
    reason_type_id = fields.Selection([
        ('ret', 'Return'),
        ('adj', 'Adjust Stock'),
    ], string='Reason Type')    
