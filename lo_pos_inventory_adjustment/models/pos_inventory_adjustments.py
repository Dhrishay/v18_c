# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#   Copyright (C) 2016-today Geminate Consultancy Services (<http://geminatecs.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import api, fields, models, _

class PosOrder(models.Model):
    _inherit = "pos.order"

    warehouse = fields.Char("warehouse")
    locataion = fields.Char("locataion")
    pda = fields.Char("pda")

class StockLocation(models.Model):
    _name = 'stock.location'
    _inherit = ['stock.location', 'pos.load.mixin']

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        fields += ['name']
        return fields

class POSInventory(models.Model):
    _inherit = 'stock.quant'

    barcode = fields.Char(
        related='product_id.barcode', string='Barcode', store=True
    )
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda x: x.env.company.currency_id
    )
    value_amount = fields.Monetary(
        'Values Amount', compute="_compute_amount",
        currency_field='currency_id'
    )
    count_amount = fields.Monetary(
        'Count Amount', compute="_compute_amount",
        currency_field='currency_id'
    )
    diff_amount = fields.Monetary(
        'Diff Amount', compute="_compute_diff_amount",
        currency_field='currency_id', store=True
    )
    employee_id  = fields.Many2one('hr.employee', string='Staff')
    date_ending  = fields.Datetime('Date Ending')
    pos_name = fields.Char('POS Name')
    warehouse_no = fields.Char('Warehouse No')
    location_no = fields.Char('Location No')
    pda = fields.Char('PDA')
    is_ready_count = fields.Boolean('Is ready count')


    def action_counted_stock(self):
        self.ensure_one()
        result = {
            "type": "ir.actions.act_window",
            "res_model": "stock.count.adjust",
            "domain": [('stock_quant_id', '=', self.id)],
            "context": {"create": False},
            "name": "Stock Counted",
            'view_mode': 'list,form',
        }
        return result

    @api.depends('quantity','inventory_quantity')
    def _compute_amount(self):
        for rec in self:
            rec.value_amount = rec.quantity * rec.product_id.standard_price
            rec.count_amount = rec.inventory_quantity * rec.product_id.standard_price

    @api.depends('quantity','inventory_quantity')
    def _compute_diff_amount(self):
        for rec in self:
            rec.diff_amount = rec.inventory_diff_quantity * rec.product_id.standard_price


class StockCountAdjust(models.Model):
    _name = 'stock.count.adjust'
    _description = 'Stock Counted Adjustment'
    _rec_name = 'display_name'

    display_name = fields.Char(
        'Display Name', compute='_compute_display_name'
    )
    pos_name = fields.Char('POS Name')
    counted_date = fields.Datetime('Date Counted')
    barcode = fields.Char(
        related='product_id.barcode', string='Barcode', store=True
    )
    product_id = fields.Many2one(
        'product.product', string='Product'
    )
    location_id = fields.Many2one(
        'stock.location', string='Location'
    )
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda x: x.env.company.currency_id
    )
    qty_onhand = fields.Float('On Hand')
    stock_values = fields.Monetary(
        'Stock Values', compute='_compute_amount_non_stored',
        currency_field='currency_id'
    )
    counted_amount = fields.Monetary(
        'Counted Amount', compute='_compute_amount_non_stored',
        currency_field='currency_id'
    )
    corrected_amount = fields.Monetary(
        'Corrected Amount', compute='_compute_amount_non_stored',
        currency_field='currency_id'
    )
    diff_qty = fields.Float(
        'Diff QTY', compute='_compute_amount_stored',
        store=True
    )
    diff_amount = fields.Monetary(
        'Diff Amount', compute='_compute_amount_stored',
        currency_field='currency_id', store=True
    )
    counted_qty = fields.Float('Counted QTY')
    corrected_qty = fields.Float('Corrected QTY')
    stock_quant_id = fields.Many2one(
        'stock.quant', string='Inventory Adjustment'
    )
    user_id = fields.Many2one('res.users', string='User')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    control_desk = fields.Char('Control Desk')
    warehouse_no = fields.Char('Warehouse No')
    location_no = fields.Char('Location No')
    pda = fields.Char('PDA')
    stock_take = fields.Char('Stock Take')
    sequence = fields.Char('SEQ')

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.product_id.name

    @api.depends('qty_onhand', 'counted_qty', 'corrected_qty')
    def _compute_amount_non_stored(self):
        """Computes non-stored fields: stock_values, counted_amount, corrected_amount"""
        for rec in self:
            rec.stock_values = rec.qty_onhand * rec.product_id.standard_price
            rec.counted_amount = rec.counted_qty * rec.product_id.standard_price
            rec.corrected_amount = rec.corrected_qty * rec.product_id.standard_price

    @api.depends('qty_onhand', 'counted_qty')
    def _compute_amount_stored(self):
        """Computes stored fields: diff_qty, diff_amount"""
        for rec in self:
            rec.diff_qty = rec.counted_qty - rec.qty_onhand
            rec.diff_amount = (rec.counted_qty * rec.product_id.standard_price) - rec.stock_values


    def action_apply_corrected_stock(self, text_pass = None):
        if self.corrected_qty <= 0 and text_pass == None:
            wizard_id = self.env['stock.corrected.wizard'].create({
                'stock_count_adjust_id': self.id,
            })
            return {        
                'name': _("Will you corrected it to 0 or Negative?"),
                'context': {'corrected_qty': self.corrected_qty},
                'view_mode': 'form',
                'res_model': 'stock.corrected.wizard',
                'res_id': wizard_id.id,
                'views': [(self.env.ref('lo_pos_inventory_adjustment.stock_corrected_wizard').id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
            }

        quant_counted_qty = self.stock_quant_id.inventory_quantity + (self.corrected_qty - self.counted_qty)
        self.stock_quant_id.inventory_quantity = quant_counted_qty
        corrected_id = self.env['stock.corrected.adjust'].search([('stock_count_id','=',self.id)],limit=1)
        if corrected_id:
            corrected_id.write({
                'corrected_date' : fields.datetime.now(),
                'counted_qty' : self.counted_qty,
                'corrected_qty' : self.corrected_qty,
                'user_id' : self.env.user.id,
            })
        else:
            corrected_id = self.env['stock.corrected.adjust'].create({
                'stock_count_id' : self.id,
                'corrected_date' : fields.datetime.now(),
                'product_id' : self.product_id.id,
                'location_id' : self.location_id.id,
                'counted_qty' : self.counted_qty,
                # 'counted_amount' : self.counted_amount,
                'corrected_qty' : self.corrected_qty,
                # 'corrected_amount' : self.corrected_amount,
                'user_id' : self.env.user.id,
                'employee_id' : self.employee_id.id,
                'warehouse_no' : self.warehouse_no,
                'location_no' : self.location_no,
                'pda' : self.pda,
            })

        self.counted_qty = self.corrected_qty
        self.corrected_qty = 0


    def action_corrected_stock(self):
        self.ensure_one()
        result = {
            "type": "ir.actions.act_window",
            "res_model": "stock.corrected.adjust",
            "domain": [('stock_count_id', '=', self.id)],
            "context": {"create": False},
            "name": "Stock Corrected",
            'view_mode': 'list,form',
        }
        return result


class StockCorrected(models.Model):
    _name = 'stock.corrected.adjust'
    _description = 'Stock Corrected Adjustment'
    _rec_name = 'display_name'

    display_name = fields.Char(
        'Display Name', compute='_compute_display_name'
    )
    pos_name = fields.Char('POS Name')
    stock_count_id = fields.Many2one(
        'stock.count.adjust', string='Stock Counted'
    )
    corrected_date = fields.Datetime('Date Corrected')
    barcode = fields.Char(
        related='product_id.barcode', string='Barcode', store=True
    )
    product_id = fields.Many2one('product.product', string='Product')
    location_id = fields.Many2one('stock.location', string='Location')
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda x: x.env.company.currency_id
    )
    counted_qty = fields.Float('Counted QTY')
    corrected_qty = fields.Float('Corrected QTY')
    counted_amount = fields.Monetary(
        'Counted Amount', compute='_compute_amount_non_stored',
        currency_field='currency_id'
    )
    corrected_amount = fields.Monetary(
        'Corrected Amount', compute='_compute_amount_non_stored',
        currency_field='currency_id'
    )
    diff_qty = fields.Float(
        'Diff QTY', compute='_compute_amount_stored',
        store=True
    )
    diff_amount = fields.Monetary(
        'Diff Amount', compute='_compute_amount_stored',
        currency_field='currency_id', store=True
    )
    user_id = fields.Many2one('res.users', string='User')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    control_desk = fields.Char('Control Desk')
    warehouse_no = fields.Char('Warehouse No')
    location_no = fields.Char('Location No')
    pda = fields.Char('PDA')
    stock_take = fields.Char('Stock Take')
    sequence = fields.Char('SEQ')

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.product_id.name

    @api.depends('corrected_qty', 'counted_qty')
    def _compute_amount_non_stored(self):
        """Computes counted and corrected amounts (non-stored)."""
        for rec in self:
            rec.counted_amount = rec.counted_qty * rec.product_id.standard_price
            rec.corrected_amount = rec.corrected_qty * rec.product_id.standard_price

    @api.depends('corrected_qty', 'counted_qty')
    def _compute_amount_stored(self):
        """Computes diff_qty and diff_amount (stored)."""
        for rec in self:
            rec.diff_qty = rec.corrected_qty - rec.counted_qty
            rec.diff_amount = rec.corrected_amount - rec.counted_amount
