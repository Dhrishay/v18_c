from odoo import fields, models

class ResCompany(models.Model):
    _inherit="res.company"

    location_id = fields.Many2one(
        'stock.location', string='Franchise Location'
    )
