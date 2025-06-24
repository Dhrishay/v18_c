from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    customer_order_date = fields.Datetime(string='Customer Order Date')
    sale_type = fields.Selection([
        ('local', 'Local Sale'),
        ('export', 'Export Sale')
    ], string='Sale Type', required=True)
    product_template_ids = fields.Many2many('product.template', compute="_compute_product_template_id", string='Products')
    
    
    @api.depends('order_line.product_template_id')
    def _compute_product_template_id(self):
        for order in self:
            order.product_template_ids = order.order_line.product_template_id
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['invoice_type'] = self.sale_type
        return invoice_vals
    
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    customer_required_date = fields.Datetime(string='Customer Required Date')
    agreed_date = fields.Datetime(string='Agreed Date')
    quantity_to_deliver = fields.Float(string='Quantity To Deliver', compute="compute_quantity_to_deliver")
    invoice_ids = fields.Many2many('account.move', 'account_sale_order_line_rel', 'sale_order_line_id', 'account_move_id')
    invoice_count = fields.Integer(compute="compute_invoice_count")
    
    @api.depends('qty_delivered')
    def compute_quantity_to_deliver(self):
        """
            Calculates the total number of quantity left to deliver
        :return: Float
        """
        for line in self:
            quantity_to_deliver = line.product_uom_qty - line.qty_delivered
            line.quantity_to_deliver = quantity_to_deliver
    
    
    def action_create_product_invoice(self):
        grouped_lines = {}
        invoice_ids = self.env['account.move']
        sale_line_ids = self.browse(self.env.context.get('active_ids'))
    
        for sale_line in sale_line_ids:
            grouped_lines.setdefault(sale_line.order_id, self.env['sale.order.line'])
            grouped_lines[sale_line.order_id] |= sale_line
    
        for order, order_lines in grouped_lines.items():
            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': order.partner_id.id,
                'invoice_date': fields.Date.today(),
                'invoice_origin': order.name,
                'invoice_line_ids': [],
                'invoice_type': order.sale_type
            }
            
            for line in order_lines:
                invoice_vals['invoice_line_ids'].append((0, 0, {
                    'product_id': line.product_id.id,
                    'quantity': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'price_subtotal': line.price_subtotal,
                    'tax_ids': [(6, 0, line.tax_id.ids)],
                    'name': line.name,
                    'sale_line_ids':line
                }))
    
            # Create the invoice
            invoice_id = self.env['account.move'].create(invoice_vals)
            invoice_ids |= invoice_id
    
            # Link the created invoice to the sale order lines
            order_lines.write({'invoice_ids': [(4, invoice_id.id)]})
    
        if invoice_ids:
            return {
                'name': 'Customer Invoice',
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'list,form',
                'domain': [('id', 'in', invoice_ids.ids)],
                'target': 'current',
            }





    @api.depends('invoice_ids')
    def compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec.invoice_ids)
            
    def action_open_invoices(self):
        return {
            'name': 'Invoices',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'domain': [('id', 'in', self.invoice_ids.ids)],
            'res_id': self.id,
            'type': 'ir.actions.act_window',
        }
    
    
    # Export Invoice Fields
    
    dbk_code = fields.Char(string="DBK Code", compute="_compute_code", store=True)
    consignee_hsn = fields.Char(string="CONSIGNEE HSN", compute="_compute_code", store=True)
    
    @api.depends('product_id')
    def _compute_code(self):
        for rec in self:
            if rec.product_template_id:
                rec.dbk_code = rec.product_template_id.dbk_code
                rec.consignee_hsn = rec.product_template_id.consignee_hsn
    
    
class SaleReportInherti(models.Model):
    _inherit = "sale.report"
    
    delivery_date_done = fields.Datetime("Effective Date", readonly=True)
    
    def _select_additional_fields(self):
        additional_fields = super()._select_additional_fields()
        additional_fields["delivery_date_done"] = """
            (SELECT MIN(sp.date_done) FROM stock_picking sp
             JOIN stock_move sm ON sm.picking_id = sp.id
             JOIN sale_order_line sol ON sol.id = sm.sale_line_id
             WHERE sol.order_id = s.id)
        """
        return additional_fields