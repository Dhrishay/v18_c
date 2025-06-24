from odoo import api, models, registry, fields, _


class ResDistrict(models.Model):
    _name = 'res.district'
    _description = 'District'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    province_id = fields.Many2one(
        'res.country.state', string="Province"
    )






