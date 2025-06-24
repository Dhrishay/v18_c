from odoo import api, fields, models


class RentalTypeAll(models.Model):
    _name = "rental.type.all"
    _description = "Rental Type All"

    line_ids = fields.One2many( comodel_name="rental.type.all.line", inverse_name="rental_type_id", string="Rental Type Lines",)

    name = fields.Char(string="Rental Type All", required=True, translate=True)
    prieclist = fields.Many2one('product.pricelist', string="Pricelist", required=True)
    currency_id = fields.Many2one('res.currency', related='prieclist.currency_id', string="Currency")
    contract_type = fields.Selection([('days', 'Days'), ('month', 'Month')], string='Contract Type', required=True,)
    image = fields.Image(string="Image")


class RentalTypeAllLine(models.Model):
    _name = "rental.type.all.line"
    _description = "Rental Type All Lines"
    _rec_name = 'location_lines'

    rental_type_id = fields.Many2one( comodel_name="rental.type.all", string="Rental Type All", ondelete="cascade",)
    location_lines = fields.Char(string="Locations", required=True)
    size_lines = fields.Char(string="Sizes", required=True)
    currency_ids = fields.Many2one('res.currency', string="Currency")
    agreed_amounts = fields.Monetary(string="Agreed Amount", currency_field="currency_ids")
    contract_type = fields.Selection([('days', 'Days'), ('month', 'Month')], string='Contract Type', required=True,)
    location_branch_id = fields.Many2one('location.branch', string="Location Branch")
