from odoo import api, fields, models

class LocationTypes(models.Model):
    _name = "location.types"
    _description = "Location Types"

    name = fields.Char(string="Location Types", required=True, translate=True)
    types_lines_ids = fields.One2many(
        comodel_name="location.types.lines",  
        inverse_name="location_type_id",     
        string="Types Lines"                 
    )

class LocationTypesLines(models.Model):
    _name = "location.types.lines"
    _description = "Location Types Lines"

    name = fields.Char(string="Line Name", required=True)
    location_type_id = fields.Many2one(
        comodel_name="location.types",     
        string="Location Type",           
        ondelete="cascade"                 
    )

    rental_area_size = fields.Char(
        comodel_name="size.tag",     
        string="Size",                     
        required=True
    )
    location_id = fields.Char(
        comodel_name="config.tag",          
        string="Location",                  
        required=True
    )
    agreed_amount = fields.Monetary(
        string="Amount",                   
        currency_field="currency_id",     
        required=True
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",       
        string="Currency",                 
        required=True,
        default=lambda self: self.env.company.currency_id
    )

class ConfigTag(models.Model):
    _name = "config.tag"
    _description = "Locations" # Config Tag

    name = fields.Char(string='Locations', required=True)
    active = fields.Boolean(string="Active", default=True)

class SizeTag(models.Model):
    _name = "size.tag"
    _description = "Size"

    name = fields.Char(string='Name', required=True)

class OwnerTag(models.Model):
    _name = "owner.tag"  
    _description = "Owner Tag"
    _rec_name = 'owner_tag_id'

    name = fields.Char(string='Owner', required=True)
    owner_tag_id = fields.Char(string="Owner Tag", required=True)
    # active = fields.Boolean(string="Active", default=True)
    # color = fields.Integer(string="Color")
    owner_image = fields.Image(string="Owner Image")
    owner_text_header = fields.Html(string="Owner Text Header", translate=True,)
    owner_text_footer = fields.Html(string="Owner Text Footer", translate=True,)

    owner_sale_order = fields.Char (string="Owner Sale Order", required=True)
    owner_contract = fields.Char (string="Owner Contract", required=True)

    contract_image_id = fields.Image(string="Owner Contract Image")
    contract_header_id = fields.Html(string="Owner Contract Header", translate=True,)

    

class LocationBranch(models.Model):
    _name = "location.branch"  
    _description = "Location Branch"

    name = fields.Char(string='Location Branch', required=True)
    

