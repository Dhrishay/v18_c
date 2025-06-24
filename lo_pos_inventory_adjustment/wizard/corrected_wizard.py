from odoo import models, fields, api, _
from datetime import datetime, timedelta
import datetime

class StockCorrected(models.TransientModel):
    _name = 'stock.corrected.wizard'
    _description = 'Stock Corrected'

    stock_count_adjust_id = fields.Many2one('stock.count.adjust',string='Stock Count')

    def _get_default_number(self):
        corrected_id = self.stock_count_adjust_id
        return str(corrected_id.corrected_qty)

    number = fields.Char('number')

    def action_confirm(self):
        corrected_id = self.stock_count_adjust_id
        corrected_id.action_apply_corrected_stock(text_pass = True)

        
   