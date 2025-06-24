# models/res_company.py
from odoo import models, fields ,api

class ResCompany(models.Model):
    _inherit = 'res.company'

    label_bg_color = fields.Char(string="Label Background Color", default="#FFA915")
    product_label_template_id = fields.Many2one(
        'ir.ui.view',
        string="Default Product Label Template",
        domain=[
            ('type', '=', 'qweb'),
            ('name', 'ilike', 'label_g')
                ],
    )
    product_label_template_name = fields.Char(
    string="Product Label Template Name",compute='_compute_template',
    help="Technical name of the QWeb template to use, e.g., 'your_module.label_template_1'",
)
     
   
    def _compute_template(self):
        for res in self:
            if res.product_label_template_id:
                res.product_label_template_name = res.product_label_template_id.xml_id
            else:
                res.product_label_template_name = False