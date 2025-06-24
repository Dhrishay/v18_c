from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    picking_type_ids = fields.Many2many(
        comodel_name='stock.picking.type',
        help="Enter Operation Type which you want to restrict from this user",
        string="Operation Types"
    )
