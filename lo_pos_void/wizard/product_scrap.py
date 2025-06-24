# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_is_zero, float_compare, convert, plaintext2html
from datetime import datetime
import time
import threading


class ProductScrapWizard(models.TransientModel):
    _name = "product.scrap.wizard"
    _description = "Product Scrap"

    def _get_default_scrap_location_id(self):
        groups = self.env['stock.location']._read_group(
            [('company_id', 'in', self.env.company.ids), ('scrap_location', '=', True)], ['company_id'], ['id:min'])
        locations_per_company = {
            company.id: stock_warehouse_id
            for company, stock_warehouse_id in groups
        }
        return locations_per_company[self.env.company.id]

    def _get_default_location_id(self):
        company_warehouses = self.env['stock.warehouse'].search([('company_id', 'in', self.env.company.ids)])
        if len(company_warehouses) == 0 and self.env.company.id:
            self.env['stock.warehouse']._warehouse_redirect_warning()
        groups = company_warehouses._read_group(
            [('company_id', 'in', self.env.company.ids)], ['company_id'], ['lot_stock_id:array_agg'])
        locations_per_company = {
            company.id: lot_stock_ids[0] if lot_stock_ids else False
            for company, lot_stock_ids in groups
        }
        return locations_per_company[self.env.company.id]

    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=True)
    location_id = fields.Many2one(comodel_name="stock.location", string="Location", default=_get_default_location_id,
                                  required=True)
    scrap_qty = fields.Float(required=True)
    reason_id = fields.Many2one('stock.scrap.reason.tag', 'Waste Reason', required=True)
    void_reason_id = fields.Many2one('void.reasons', 'Void Reason')
    extra_note = fields.Text('Extra Note')
    scrap_location_id = fields.Many2one(
        'stock.location', 'Scrap Location', default=_get_default_scrap_location_id,
        domain="[('scrap_location', '=', True)]", required=True)
    scrap_id = fields.Many2one('stock.scrap', string='Waste')

    def _should_check_available_qty(self):
        return self.product_id.is_storable

    def check_available_qty(self, order_line, flag):
        if not order_line.product_id.is_storable:
            return True
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        available_qty = order_line.with_context(
            location=self.location_id.id,
            lot_id=False,
            package_id=False,
            owner_id=False,
            strict=True,
        ).product_id.qty_available

        scrap_qty = order_line.product_uom_id._compute_quantity(self.scrap_qty, order_line.product_id.uom_id)
        return float_compare(available_qty, scrap_qty, precision_digits=precision) >= 0

    def _prepare_move_values(self, scrap):
        self.ensure_one()
        return {
            'name': scrap.name,
            'origin': scrap.name,
            'company_id': scrap.company_id.id,
            'product_id': scrap.product_id.id,
            'product_uom': scrap.product_uom_id.id,
            'state': 'draft',
            'product_uom_qty': scrap.scrap_qty,
            'location_id': scrap.location_id.id,
            'scrapped': True,
            'scrap_id': scrap.id,
            'location_dest_id': scrap.scrap_location_id.id,
            'move_line_ids': [(0, 0, {
                'product_id': scrap.product_id.id,
                'product_uom_id': scrap.product_uom_id.id,
                'quantity': scrap.scrap_qty,
                'location_id': scrap.location_id.id,
                'location_dest_id': scrap.scrap_location_id.id,
            })],
            'picked': True,
        }

    def do_scrap(self, order_line, flag):
        scrap_id = self.env['stock.scrap'].create({
            'product_id': self.product_id.id,
            'product_uom_id': order_line.product_uom_id.id if not flag else order_line.product_id.uom_id.id,
            'scrap_qty': self.scrap_qty,
            'location_id': self.location_id.id,
            'scrap_location_id': self.scrap_location_id.id,
            'scrap_reason_tag_ids': [(4, self.reason_id.id)],
            'extra_note': self.extra_note
        })
        for scrap in scrap_id:
            scrap.name = self.env['ir.sequence'].next_by_code('stock.scrap') or _('New')
            move = self.env['stock.move'].create(self._prepare_move_values(scrap))
            move.with_context(is_scrap=True)._action_done()
            scrap.write({'state': 'done'})
            scrap.date_done = fields.Datetime.now()
            if not flag:
                order_line.is_scraped = True
            order_line.scrap_id = scrap.id
        return scrap_id

    def action_validate(self):
        self.ensure_one()
        order_line = self.env['pos.order.line'].browse(self.env.context.get('active_id'))
        if self.scrap_qty < 0 or float_is_zero(self.scrap_qty,
                                               precision_rounding=order_line.product_uom_id.rounding):
            raise UserError(_('You Can Only Enter Positive Value In Quantity.'))
        if self.scrap_qty > order_line.qty:
            raise UserError(_('Waste quantity should not greater than actual quantity.'))

        if self.check_available_qty(order_line, False):
            order_line.update({'status': 'waste'})
            self.env.user.sudo()._bus_send("action_pad_update", {'data': []})
            return self.do_scrap(order_line, False)
        else:
            raise UserError(_('Not Waste'))

    def action_validate_scrap(self):
        self.ensure_one()
        void_id = self.env['pos.void.reason.history'].browse(self.env.context.get('active_id'))
        if self.scrap_qty < 0 or float_is_zero(self.scrap_qty,
                                               precision_rounding=self.product_id.uom_id.rounding):
            raise UserError(_('You Can Only Enter Positive Value In Quantity.'))
        if self.scrap_qty > void_id.qty:
            raise UserError(_('Waste quantity should not greater than actual quantity.'))

        if self.check_available_qty(void_id, True):
            return self.do_scrap(void_id, True)
        else:
            raise UserError(_('Not Waste'))

    def action_validate_waste_and_void(self):
        self.ensure_one()
        order_line = self.env['pos.order.line'].browse(self.env.context.get('active_id'))
        if self.scrap_qty < 0 or float_is_zero(self.scrap_qty,
                                               precision_rounding=order_line.product_uom_id.rounding):
            raise UserError(_('You Can Only Enter Positive Value In Quantity.'))

        if self.scrap_qty > order_line.qty:
            raise UserError(_('Waste quantity should not greater than actual quantity.'))

        if self.check_available_qty(order_line, False):
            scrap_id = self.do_scrap(order_line, False)
            void_vals = {
                'pos_order_id': order_line.order_id.id,
                'reason_id': self.void_reason_id.id,
                'session_id': order_line.order_id.session_id.id,
                'product_id': self.product_id.id,
                'price': order_line.price_unit,
                'order_no': order_line.order_id.name,
                'table_no': order_line.order_id.table_id.table_number if order_line.order_id.table_id else '',
                'extra_note': self.extra_note,
                'date': datetime.now(),
                'pos_config_id': order_line.order_id.config_id.id,
                'user_id': order_line.order_id.user_id.id if order_line.order_id.user_id else False,
                'employee_id': order_line.cashier_id.id if order_line.cashier_id else False,
                'qty': order_line.qty,
            }
            void_id = self.env['pos.void.reason.history'].create(void_vals)
            void_id.update({'scrap_id': scrap_id.id})
            order_line.update({'status': 'waste_and_void'})
            order_line.unlink()
            self.env.user.sudo()._bus_send("wast_from_backend", {'data': []})

        else:
            raise UserError(_('Not Waste'))