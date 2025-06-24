#get this model code form lod_batch_update_price module to set the update batch price
from odoo import api,models, fields
from datetime import datetime, timedelta 
import datetime


class BatchUpdatePrice(models.Model):
    _name = "batch.update.price"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Batch Update Price"
    _rec_name="name"
     
    name = fields.Char('name',required=True)
    product_id = fields.Many2one(
        'product.template',
        related='batch_line_ids.product_id', string='Product'
    )
    batch_line_ids = fields.One2many(
        'batch.update.price.line','batch_id',
        string='Batch Line',tracking=True
    )
    user_update_id = fields.Many2one(
        'res.users', string="User Update",
        tracking=True
    )
    date_update = fields.Datetime(
        string="New Date Updated", tracking=True
    )
    dat_update = fields.Date(string="Date for Update", tracking=True)
    status = fields.Selection(([
        ('draft','Draft'),
        ('appove','Appove'),
        ('updated','Updated')
    ]), default='draft', string="Status",tracking=True)

    def auto_update_batch_price(self):
        to_day = fields.Datetime.now() + datetime.timedelta(hours=7)
        batch_price = self.search([
            ('status', '=', 'appove'),
            ('dat_update', '=', to_day.date())]
        )
        for order in batch_price:
            for line in order.batch_line_ids:
                line.product_id.write({
                    'list_price': line.update_sale_price,
                    'standard_price': line.update_cost_price,
                    })
                line.write({'status':'updated'})
            order.status = 'updated'
            order.user_update_id = order.env.uid
            order.date_update = fields.Datetime.now()

    def action_batch_update_price(self):
        for line in self.batch_line_ids:
            line.product_id.write({
                'list_price': line.update_sale_price,
                'standard_price': line.update_cost_price,
                })
            line.write({'status':'updated'})
                                    
        self.status = 'updated'
        self.user_update_id = self.env.uid
        self.date_update = fields.Datetime.now()
        self.dat_update = fields.Datetime.now()
        self.write({'status':'updated'})

    def resettodaft(self):
        self.status='draft'
        for rec in self.batch_line_ids:
            line=self.env['batch.update.price.line'].browse(rec.id)
            line.write({'status':'draft'})

    @api.model_create_multi
    def create(self, vals_list):
        records = super(BatchUpdatePrice, self).create(vals_list)
        for record in records:
            record.date_update = fields.Datetime.now()
        return records

    def write(self, vals): 
        vals['date_update'] = fields.Datetime.now() 
        return super(BatchUpdatePrice, self).write(vals)

    def appove(self):
        self.status='appove'  
        self.user_update_id = self.env.uid
        self.date_update = fields.Datetime.now()
        self.dat_update = fields.Datetime.now()
        for rec in self.batch_line_ids:
            line=self.env['batch.update.price.line'].browse(rec.id)
            line.write({'status':'appove'})


class BatchUpdatePriceLine(models.Model):
    _name='batch.update.price.line'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description='Batch Update price line'
    
    batch_id = fields.Many2one(
        'batch.update.price', string='Order Reference'
    )
    status = fields.Selection([
        ('draft','Draft'),
        ('appove','Appove'),
        ('updated','Updated')
    ], default='draft', string="Status")
    product_id = fields.Many2one(
        'product.template', string="Product ID",
        required=True, tracking=True
    )
    product_barcode = fields.Char(
        related='product_id.barcode', string="Product Barcode"
    )
    current_sale_price = fields.Float(
        readonly=True, string="Current Sale Price"
    )
    update_sale_price = fields.Float(
        string="Update Sale Price", tracking=True
    )
    margin_sale_price = fields.Float(
        string="Margin Sale Price", readonly=True,
        compute='_compute_sale_price'
    )
    current_standard_price = fields.Float(
        readonly=True, string="Current Cost Price"
    )
    update_cost_price = fields.Float(
        string="Update Cost Price", tracking=True
    )
    margin_cost_price = fields.Float(
        string="Margin Cost Price", readonly=True,
        compute='_compute_standard_price'
    )
    schedule_update = fields.Datetime(
        string="Schedule Date", default=fields.Datetime.now(),
        tracking=True
    )
    uom_id = fields.Many2one(
        related='product_id.uom_id', string="Unit of Measure",
        store=True
    )
    barcode = fields.Char("Barcode")

    def _compute_sale_price(self):
        for so in self:
            if so.current_sale_price==0: 
                so.margin_sale_price=1
            else:
                so.margin_sale_price=((so.update_sale_price-so.current_sale_price)/so.current_sale_price)

    def _compute_standard_price(self):
        for so in self:
            if so.current_standard_price==0: 
                so.margin_cost_price=1
            else:
                so.margin_cost_price=((so.update_cost_price-so.current_standard_price)/so.current_standard_price)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.current_sale_price=self.product_id.list_price
        self.current_standard_price=self.product_id.standard_price

    @api.model_create_multi
    def create(self, vals_list):
        records=super(BatchUpdatePriceLine, self).create(vals_list)
        for record in records:
            product = self.env['product.template'].browse(record.product_id.id)
            record.current_sale_price = product.list_price
            record.current_standard_price = product.standard_price
        return records

    @api.onchange('barcode')
    def onhcange_barcode(self):
        for rec in self:
            if rec.barcode:
                product_id = self.env['product.product'].sudo().search([
                    ('barcode','=',rec.barcode)
                ])
                if not product_id:
                    barcode_id = self.env['product.barcode.multi'].sudo().search([
                        ('name','=',rec.barcode)
                    ])
                    if len(barcode_id):
                        product_id = barcode_id[0].product_id
                if product_id:
                   rec.product_id = product_id.id

    @api.onchange('product_id','barcode')
    def batch_line_product_id_onchange(self):
        if self.product_id and not self.barcode:
            if self.product_id.barcode:
                self.barcode = self.product_id.barcode
            elif len(self.product_id.barcode_ids) > 0:
                self.barcode = self.product_id.barcode_ids[0].name
