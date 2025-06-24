from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    request_type = fields.Boolean(string='Request Type',default=False)
    return_request_type = fields.Boolean(string='Return Request Type',default=False)


class StockPickingLines(models.Model):
    _inherit = 'stock.move'

    quantity_exceeded = fields.Boolean(string='quantity_exceeded', store=False)

    @api.onchange('quantity','product_uom_qty')
    def _onchange_quantity_receipt(self):
        for res in self:
            if res.quantity > res.product_uom_qty:
                raise UserError("ຈຳນວນຮັບເຂົ້າ ຫຼາຍກ່ວາຈຳນວນທີ່ຕ້ອງການ")
            if res.quantity < res.product_uom_qty:
                res.quantity_exceeded = True
            if res.quantity == res.product_uom_qty:
                res.quantity_exceeded = False
