#This code is getting from lod_kokkokm module
import math
from odoo import api, fields, models
from check_digit_EAN13.check_digit import get_check_digit


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def roundup_amount(self, amount):
        fee = str(amount)
        last_three = fee[-3:]
        if int(last_three) <= 200 and int(last_three) > 0:
            return int(math.ceil(amount / 500.0)) * 500 - 500
        elif int(last_three) > 200 and int(last_three) <= 500:
            return int(math.ceil(amount / 500.0)) * 500
        elif int(last_three) > 500 and int(last_three) <= 700:
            return int(math.ceil(amount / 500.0)) * 500 - 500
        elif int(last_three) > 700 and int(last_three) <= 999:
            return int(math.ceil(amount / 500.0)) * 500
        else:
            return math.ceil(amount)

    def _compute_sale_count(self):
        for product in self:
            if product.sales_count >= 1000:
                product.top_pog = 'A'
            elif product.sales_count >= 500:
                product.top_pog = 'B'
            elif product.sales_count >= 100:
                product.top_pog = 'C'
            else:
                product.top_pog = False

    serial_no  = fields.Char('Serial Number', copy=False)
    model_field = fields.Char('Model ID', copy=False)
    country_id = fields.Many2one(
        'res.country', string="Country"
    )
    country_import_id = fields.Many2one(
        'lod.country.import', string="Country Import"
    )
    partner_id = fields.Many2one(
        'res.partner', string="Partner"
    )
    top_pog = fields.Selection([
            ('A', 'A Top 100'),
            ('B', 'B Top 500'),
            ('C', 'C Top 1000'),
        ], string='Top POG' ,compute="_compute_sale_count"
    )

    _sql_constraints = [
        (
            'model_field', 'unique (model_field)',
            "The Model ID must be unique, this one is already assigned to another (model_field)."
        )
    ]
    _sql_constraints = [
        (
            'serial_no', 'unique (serial_no)',
            "The Model ID must be unique, this one is already assigned to another (serial_no)."
        )
    ]

    is_product_discount = fields.Boolean('Discount')
    new_cost = fields.Float('New Cost', digits=(16, 2))
    margin_percent = fields.Float('Margin %', digits=(16, 2))
    margin_amount = fields.Float('Margin Amt', digits=(16, 2))
    markup_percent = fields.Float('Markup %', digits=(16, 2))
    markup_amount = fields.Float('Markup Amt', digits=(16, 2))
    old_sale_price = fields.Float('Old Sale Price', digits=(16, 2))
    final_sale_price = fields.Float('Final Sale Price', digits=(16, 2))
    competitor_cost_1 = fields.Float('Competitor 1')
    competitor_perc_1 = fields.Float('Comp1(%)')
    competitor_cost_2 = fields.Float('Competitor 2')
    competitor_perc_2 = fields.Float('Comp2(%)')
    competitor_cost_3 = fields.Float('Competitor 3')
    competitor_perc_3 = fields.Float('Comp3(%)')
    competitor_cost_4 = fields.Float('Competitor 4')
    competitor_perc_4 = fields.Float('Comp4(%)')
    competitor_cost_5 = fields.Float('Competitor 5')
    competitor_perc_5 = fields.Float('Comp5(%)')
    last_update = fields.Datetime('Updated')
    last_update_cost = fields.Datetime('Last Cost Updated')
    last_approved = fields.Datetime('Approved')
    price_status = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('updated_cost', 'Cost Updated'),
            ('updated', 'Updated'),
            ('checked', 'Checked'),
        ], string='Status',
        default='pending'
    )

    dif_sale_price = fields.Float(
        'Dif', compute='_compute_dif_sale_price'
    )
    dif_sale_percent = fields.Float(
        'Dif %', compute='_compute_dif_sale_price'
    )
    diff_cost_sale = fields.Float(
        'Diff', compute='_compute_dif_sale_price'
    )
    #added this fields from module kkm_branch
    product_name_la = fields.Char(
        string='Product Name(LA)',
        compute='_compute_product_name_la',
    )

    @api.depends('product_variant_id')
    def _compute_product_name_la(self):
        for record in self:
            if record.product_variant_id:
                # Set the lang context to 'lo_LA' for the related field
                product_name_la = record.product_variant_id.with_context(lang='lo_LA').name
                record.product_name_la = product_name_la
            else:
                record.product_name_la = False 

    @api.depends('new_cost', 'final_sale_price')
    def _compute_dif_sale_price(self):
        for rec in self:
            rec.dif_sale_price = rec.list_price - rec.final_sale_price
            if rec.final_sale_price == 0:
                rec.dif_sale_percent = 0
            else:
                rec.dif_sale_percent = -1 * (rec.dif_sale_price * 100 / rec.final_sale_price)
            rec.diff_cost_sale = rec.list_price - rec.standard_price

    def action_update_sale_price(self):
        for rec in self:
            rec.old_sale_price = rec.list_price
            rec.list_price = rec.final_sale_price
            rec.last_update = fields.Datetime.now()
            rec.price_status = 'updated'

    def action_update_new_cost(self):
        for rec in self:
            rec.standard_price = rec.new_cost
            rec.price_status = 'updated_cost'
            rec.last_update_cost = fields.Datetime.now()

    def action_approve_sale_price(self):
        for rec in self:
            rec.last_approved = fields.Datetime.now()
            rec.price_status = 'approved'

    def action_update_competitor_price(self):
        for rec in self:
            competitor_id = self.env['x.tmp_competitor'].search([('x_name','=',rec.barcode)])
            for comp in competitor_id:
                rec.competitor_cost_1 = comp.x_competitor_1
                rec.competitor_cost_2 = comp.x_competitor_2
                rec.competitor_cost_3 = comp.x_competitor_3
                rec.competitor_cost_4 = comp.x_competitor_4
                rec.competitor_cost_5 = comp.x_competitor_5

    @api.onchange('categ_id')
    def onchange_categ_id(self):
        if self.categ_id.categ_public_id:
            self.update({'public_categ_ids':[self.categ_id.categ_public_id.id]})
        else:
            self.update({'public_categ_ids': False})

    @api.onchange('barcode')
    def _onchange_barcode(self):
        barcode = self.barcode
        if barcode != False:
            if len(barcode) == 12 and barcode[:2] == '21':
                actual_barcode = get_check_digit(barcode)
                self.barcode = actual_barcode
   
    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if 'barcode' in values:
                barcode = values['barcode']
                if barcode and len(barcode) == 12 and barcode[:2] == '21':
                    values['barcode'] = get_check_digit(barcode)

        res = super(ProductTemplate, self).create(vals_list)
        return res


class CountryImport(models.Model):
    _name = "lod.country.import"
    _description = "Country Import"

    name = fields.Char('Name', required=True)
    margin_ids = fields.Many2many(
        'lod.margin.config', string='Margin'
    )


class MarginConfiguration(models.Model):
    _name = "lod.margin.config"
    _description = "Margin Configuration"

    name = fields.Char('Name', required=True)
    uom_id = fields.Many2one('uom.uom', string='UOM')
    margin_percent = fields.Float('Margin Percent')
    markup_percent = fields.Float(
        'Markup Percent', digits=(16, 2), compute='_compute_margin_percent'
    )

    @api.depends('margin_percent')
    def _compute_margin_percent(self):
        for rec in self:
            rec.markup_percent = ((rec.margin_percent/100) / (1 - (rec.margin_percent/100)))*100
