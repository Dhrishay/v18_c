from odoo import models, fields, api


class ReportDownloadWizard(models.TransientModel):
    _name = 'report.download.wizard'
    _description = "Report Download Wizard"

    num_expiry_days = fields.Integer(string="Product Expiry In Next")
    location_ids = fields.Many2many('stock.location', string="Location",
                                    domain=[('usage', '=', 'internal')])
    category_ids = fields.Many2many('product.category', string="Category")
    product_ids = fields.Many2many('product.product', string="Product")
    group_by = fields.Selection([
                                ('location', 'Location'), 
                                 ('category', 'Category'),
                                 ('product', 'Product'),
                                 ],
                                string="Group By",
                                default="location")
    
    all_company = fields.Boolean('All Company')
    
    company_ids = fields.Many2many('res.company',string='Company')

    @api.onchange('all_company')
    def _onchange_all_company(self):
        if self.all_company:
            self.company_ids = self.env['res.company'].search([]).ids
        else:
            self.company_ids = False

    def print_pdf_report(self):
        datas = {
            'data':self.read()[0],
        }
        return self.env.ref('lod_product_expiry_report.product_expiry_report').report_action(self, data=datas)
