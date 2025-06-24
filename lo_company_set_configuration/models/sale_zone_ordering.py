from odoo import api, models, registry, fields, _


class SaleZoneOrdering(models.Model):
    _name = 'sale.zone.ordering'
    _description = 'Zone'

    name = fields.Char(string="Name")
    time_start = fields.Float(string="Start Time")
    code_zone = fields.Char(string="Code Zone")
    time_end = fields.Float(string="To Time")
    ship_within = fields.Integer(string="Ship Within")




