from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    dbk_code = fields.Char(string="DBK Code")
    consignee_hsn = fields.Char(string="CONSIGNEE HSN")
    

class ProductProduct(models.Model):
    _inherit = "product.product"
    
    dbk_code = fields.Char(string="DBK Code")
    consignee_hsn = fields.Char(string="CONSIGNEE HSN")