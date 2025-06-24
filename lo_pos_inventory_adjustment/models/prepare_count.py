from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PrepareCount(models.Model):
    _name = 'stock.prepare.count'
    _description = 'Stock Prepare Count'
    
    barcode = fields.Char(string='Barcode')
    product_name = fields.Char(string='Product')
    location_id = fields.Many2one('stock.location', string='Location')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('updated', 'Updated')
    ], default='draft', string='Status')

    def action_set_ready_count(self):
        for rec in self:
            product_id = self.env['product.product'].sudo().search([('barcode','=',rec.barcode)])
            if product_id.id == False:
                 raise ValidationError(_(
                    'It is not have Barcode: %s, Produc name: %s') % (rec.barcode,rec.product_name)
                 )
            stock_quant_id = self.env['stock.quant'].sudo().search([
                ('product_id','=',product_id.id),
                ('location_id','=',rec.location_id.id),
                ('lot_id','=',False)], limit=1
            )
            if stock_quant_id.id:
                quant_write = stock_quant_id.sudo().write({
                    'is_ready_count': True
                })
            else:
                values = {
                    'product_id': product_id.id,
                    'location_id': rec.location_id.id,
                    'user_id': rec.env.user.id,
                    'inventory_quantity': 0,
                    'is_ready_count': True
                }
                quant_create = rec.env['stock.quant'].sudo().create(values)

            rec.state = 'updated'
        