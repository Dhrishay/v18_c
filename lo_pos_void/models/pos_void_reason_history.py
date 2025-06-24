# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class VoipReasonHistory(models.Model):
    _name = "pos.void.reason.history"
    _description = "Pos Void Reason History"

    pos_order_id = fields.Many2one('pos.order', string='Order')
    order_no = fields.Char('Order Number')
    table_no = fields.Char('Table Number')
    session_id = fields.Many2one('pos.session', string="Session")
    reason_id = fields.Many2one('void.reasons', 'Reason')
    date = fields.Datetime('Date')
    product_id = fields.Many2one('product.product', 'Product')
    price = fields.Float('Price')
    pos_config_id = fields.Many2one('pos.config', string="POS Name")
    extra_note = fields.Text(string='Exrta Note')
    employee_id = fields.Many2one('hr.employee','Cashier')
    user_id = fields.Many2one('res.users','User')
    qty = fields.Float('Quantity')
    scrap_id = fields.Many2one('stock.scrap',string='Waste')
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', readonly=True)
    status = fields.Selection([
        ('new','New'), ('confirm','Confirm'),
        ('waste','Waste'), ('void','Void'),
        ('waste_and_void','Waste & void')
    ])

    @api.model
    def _load_pos_data_domain(self):
        return []

    @api.model
    def _load_pos_data_fields(self):
        return ['pos_order_id', 'pos_config_id', 'order_no', 'table_no', 'session_id', 'reason_id', 'date',
                'product_id', 'price', 'extra_note','user_id','employee_id','qty','product_uom_id']

    def _load_pos_data(self, data):
        domain = self._load_pos_data_domain()
        fields = self._load_pos_data_fields()
        return {
            'data': self.search_read(domain, fields, load=False),
            'fields': self._load_pos_data_fields(),
        }

    def scrap_product(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Waste',
            'res_model': 'product.scrap.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_product_id': self.product_id.id,
                'order_id':self,
                'only_srcap':True,
                'from_void':True
            },
        }