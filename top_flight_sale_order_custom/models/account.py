from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

class AccountMove(models.Model):
    _inherit = "account.move"
    
    tax_rate = fields.Float(string="Tax Rate")
    tax_amount = fields.Monetary(string="IGST Amount", compute="_compute_taxes")
    total_tax = fields.Monetary(string="Total Tax", compute="_compute_taxes")

    def action_post(self):
        def _get_fiscal_year():
            current_year = datetime.today().year
            next_year = current_year + 1
            return f"{current_year}-{str(next_year)[-2:]}"

        for record in self:
            fiscal_year = _get_fiscal_year()

            if record.invoice_type == 'local':
                seq = self.env['ir.sequence'].next_by_code('account.move.local')
                record.name = f"TFI/{fiscal_year}/{seq[-3:]}" if seq else False
            elif record.invoice_type == 'export':
                seq = self.env['ir.sequence'].next_by_code('account.move.export')
                record.name = f"EXP/{fiscal_year}/{seq[-3:]}" if seq else False
            elif record.invoice_type == 'rodtep':
                seq = self.env['ir.sequence'].next_by_code('account.move.rodtpe')
                record.name = f"RoDTEP/{fiscal_year}/{seq[-3:]}" if seq else False

        return super(AccountMove, self).action_post()

    # def get_report_template(self, report_type):
    #     """Dynamically select the correct report based on invoice_type."""
    #     self.ensure_one()
    #     if self.invoice_type == 'local':
    #         return self.env.ref('sale_order_custom.local_invoice_report')
    #     return super().get_report_template(report_type)

    @api.depends("invoice_line_ids", "currency_id")
    def _compute_taxes(self):
        """Compute IGST and total tax for invoice."""
        
        tax_id = self.env.ref("account.1_igst_sale_18_sez_exp")

        if not tax_id:
            raise ValidationError("Tax '18% IGST S (SZ/EX)' not found.")
        
        for rec in self:
            rec.tax_rate = 0.0
            rec.tax_amount = 0.0
            rec.total_tax = 0.0
            
            for line in rec.invoice_line_ids:
                if tax_id.id in line.tax_ids.ids:
                    subtotal = line.price_subtotal
                    
                    taxes = tax_id.compute_all(subtotal, currency=rec.currency_id, quantity=line.quantity)
    
                    igst_amount = [tax.get('amount') for tax in taxes.get('taxes')][0]
            
                    rec.tax_rate = tax_id.amount
                    rec.tax_amount += igst_amount
            
            if rec.currency_id.name == 'USD':
                rate_id = rec.currency_id.rate_ids.sorted('name', reverse=True)[:1]
                rec.tax_amount *= rate_id.inverse_company_rate if rec.currency_id.rate_ids else 1.0
                rec.total_tax = rec.tax_amount
            else:
                rec.total_tax = rec.tax_amount
            

    invoice_type = fields.Selection([
        ('local', 'Local Sale'),
        ('export', 'Export Sale'),
        ('rodtep', 'RoDTEP')
    ], string='Sale Type',required="True")

    # ------------------------- Export Invoice Report Fields ---------------------
    
    reverse_charge = fields.Char(string="Reverse Charge")
    ie_code = fields.Char(string="IE Code", default="0714900290")
    attention_partner_id = fields.Many2one("res.partner", string="Kind Attention")
    goods_origin = fields.Char(string="Origin of Goods")
    destination = fields.Char(string="Final Destination")
    transport_means = fields.Char("Vessel/Flight")
    loading_port = fields.Char(string="Port of Loading")
    discharge_port = fields.Char(string="Port of Discharge")
    
    delivery_terms = fields.Char(string="Terms of Delivery")
    pre_carriage = fields.Char(string="Pre-Carriage By")
    receipt_place = fields.Char(string="Place of Receipt")
    total_box = fields.Integer(string="Total Number of Box")
    gross_weight = fields.Char(string="Gross Weight")
    net_weight = fields.Char(string="Net Weight")
    box_size = fields.Char(string="Box Size")
    remark = fields.Text(string="Remark")
    
    irn_number = fields.Char(string="IRN Number")
    ack_number = fields.Char(string="Ack Number")
    ack_date = fields.Date(string="Ack Date")
    
    inverse_invoice_currency_rate = fields.Float(
        string='Inverse Currency Rate',
        compute='_compute_inverse_invoice_currency_rate', store=True,
    )
    
    @api.depends('currency_id', 'company_currency_id', 'company_id',)
    def _compute_inverse_invoice_currency_rate(self):
        for move in self:
            if move.is_invoice(include_receipts=True):
                if move.currency_id:
                    move.inverse_invoice_currency_rate = self.env['res.currency']._get_conversion_rate(
                        from_currency=move.currency_id,
                        to_currency=move.company_currency_id,
                        company=move.company_id,
                        date=move._get_invoice_currency_rate_date(),
                    )
                else:
                    move.invoice_currency_rate = 1
    
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    dbk_code = fields.Char(string="DBK Code", compute="_compute_code", store=True)
    consignee_hsn = fields.Char(string="CONSIGNEE HSN", compute="_compute_code", store=True)
    
    @api.depends('product_id')
    def _compute_code(self):
        for rec in self:
            if rec.product_id:
                rec.dbk_code = rec.product_id.dbk_code
                rec.consignee_hsn = rec.product_id.consignee_hsn
                