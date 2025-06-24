from odoo import fields, models, api, _
from odoo.exceptions import UserError


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    @api.model_create_multi
    def create(self, vals):
        if self.env.user.has_group('eg_stock_picking_type_restriction.stock_picking_type_restriction_for_partner'):
            raise UserError(_("You don't have access to create Operation Type."))
        else:
            return super(StockPickingType, self).create(vals)

    def write(self, vals):
        res = super(StockPickingType, self).write(vals)
        if self.env.user.has_group('eg_stock_picking_type_restriction.stock_picking_type_restriction_for_partner'):
            raise UserError(_("You don't have access to Edit Operation Type."))
        else:
            return res
