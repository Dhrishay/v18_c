from odoo import models, fields, api



class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    plu = fields.Char('PLU Scale', copy=False,)
    _sql_constraints = [('plu', 'unique (plu)', "The Model ID must be unique, this one is already assigned to another (plu).")]