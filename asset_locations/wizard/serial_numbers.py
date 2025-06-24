from odoo import api, fields, models


class SerialNumbers(models.TransientModel):
    _name = "serial.numbers"
    _description = "Serial Numbers"


    name = fields.Char()
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,default=lambda self: self.env.company
    ) 
