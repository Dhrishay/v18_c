from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    is_lock_location = fields.Boolean(string="Lock Destination Location",default=False)

    def _get_fields_stock_barcode(self):
        data = super(StockPickingType, self)._get_fields_stock_barcode()
        data.append('is_lock_location')
        return data
