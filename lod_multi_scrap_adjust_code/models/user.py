from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = "res.users"
    
    stock_location_ids = fields.Many2many('stock.location', string='Stock Location')


class ResCompany(models.Model):
    _inherit="res.company"


    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type')
