from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError, ValidationError


class ReturnRequestOrder(models.TransientModel):
    _name = 'return.request.order'
    _description = 'Stock Return Picking'


    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.context.get('active_id') and self.env.context.get('active_model') == 'purchase.order':
            if len(self.env.context.get('active_ids', [])) > 1:
                raise UserError(_("You may only return one Purchase order at a time."))
            purchase = self.env['purchase.order'].browse(self.env.context.get('active_id'))
            if purchase.exists():
                res.update({'purchase_id': purchase.id})
        return res

    purchase_id = fields.Many2one('purchase.order')
    product_return_moves = fields.One2many('stock.return.line', 'wizard_id', 'Purchase Return Order', compute='_compute_moves_locations', precompute=True, readonly=False, store=True)
    company_id = fields.Many2one(related='purchase_id.company_id')


    @api.depends('purchase_id')
    def _compute_moves_locations(self):
        for wizard in self:
            product_return_moves = [Command.clear()]
            line_fields = list(self.env['stock.return.line']._fields)
            product_return_moves_data_tmpl = self.env['stock.return.line'].default_get(line_fields)
            for purchase in wizard.purchase_id.order_line:
                product_return_moves_data = dict(product_return_moves_data_tmpl)
                product_return_moves_data.update(wizard._prepare_stock_return_picking_line_vals_from_move(purchase))
                product_return_moves.append(Command.create(product_return_moves_data))
            if wizard.purchase_id and not product_return_moves:
                raise UserError(_("No products to return (only lines in Done state and not fully returned yet can be returned)."))
            if wizard.purchase_id:
                wizard.product_return_moves = product_return_moves

    @api.model
    def _prepare_stock_return_picking_line_vals_from_move(self, purchase):
        return {
            'product_id': purchase.product_id.id,
            'quantity': purchase.product_qty,
            'purchase_id': purchase.order_id.id,
            'uom_id': purchase.product_id.uom_id.id,
        }

    def action_create_returns(self):
        for return_line in self.product_return_moves:
            for purchase_line in self.purchase_id.order_line:
                if purchase_line.qty_received > 0:
                    if return_line.quantity == 0 or return_line.quantity < 0:
                        raise UserError(_("Please add product quantity greater than 0.0 ."))
                    if return_line.quantity > purchase_line.qty_received:
                        raise UserError(_("You can not return order."))
                    if purchase_line.qty_retutned > 0:
                        total = purchase_line.qty_retutned + return_line.quantity
                        if total > purchase_line.qty_received:
                            raise UserError(_("You can not return product."))
                        else:
                            purchase_line.update({'qty_retutned': total})
                    elif purchase_line.qty_retutned == 0.0:
                        if return_line.product_id.id == purchase_line.product_id.id:
                            purchase_line.update({'qty_retutned': return_line.quantity})
                else:
                    raise UserError(_("You can not return product. Product is not received yet"))

        SaleOrder = self.env['sale.order']
        SaleOrderLine = self.env['sale.order.line']
        sale_id = SaleOrder.create({
            "partner_id": self.purchase_id.partner_id.id,
            "request_type": True,
            "return_request_type": True,
            "is_without_price": True,
            "auto_purchase_order_id": self.purchase_id.id,
            "company_id": self.purchase_id.company_id.id,
        })

        for return_line in self.product_return_moves:
            SaleOrderLine.create({
                'product_id': return_line.product_id.id,
                'product_uom_qty': return_line.quantity,
                'order_id': sale_id.id,
                'price_unit': 0.0,
                'cr_sale_price': 0.0,
            })

        self.purchase_id.is_retutned = True
        return {
            'name': _('Return Request'),
            'res_model': 'sale.order',
            'res_id': sale_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('lod_request_product_to_dc.delivery_order_form').id,
            'domain': [('retrun_request_type', '=', True), ('request_type', '=', True)],
            'context': {'default_retrun_request_type': True, "default_request_type": True,},
            'type': 'ir.actions.act_window',
        }


class ReturnRequestOrderLine(models.TransientModel):
    _name = 'stock.return.line'
    _description = 'Stock Return Line'


    product_id = fields.Many2one('product.product', string="Product", required=True)
    quantity = fields.Float("Quantity", digits='Product Unit of Measure', default=1, required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', related='product_id.uom_id')
    wizard_id = fields.Many2one('return.request.order', string="Wizard")
    purchase_id = fields.Many2one('purchase.order', "Purchases")
