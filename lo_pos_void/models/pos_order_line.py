# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_
from odoo.tools import float_is_zero, float_compare, convert, plaintext2html
from odoo.exceptions import ValidationError,UserError


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

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

    is_scraped = fields.Boolean("Scraped")
    scrap_id = fields.Many2one('stock.scrap',string='Waste')
    same_line_id = fields.Char('Same Product')
    cashier_id = fields.Many2one('hr.employee','Cashier')
    barcode = fields.Char(
        string='Barcode',
        related='product_id.barcode',
    )
    
    def export_as_JSON(self):
        res = super().export_as_JSON()
        res['barcode'] = self.product_id.barcode or ""
        return res    

    def button_scrap(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Waste',
            'res_model': 'product.scrap.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_product_id': self.product_id.id,'order_id':self,'only_srcap':True},

        }

    def button_scrap_and_void(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Waste And Void',
            'res_model': 'product.scrap.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_product_id': self.product_id.id,'order_id':self},

        }

    def _should_check_available_qty(self,order_line):
        return order_line.product_id.is_storable

    def check_available_qty(self,order_line):
        if not order_line.product_id.is_storable:
            return True
        location_id = self._get_default_location_id()
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        available_qty = order_line.with_context(
            location=location_id,
            lot_id=False,
            package_id=False,
            owner_id=False,
            strict=True,
        ).product_id.qty_available
        scrap_qty = order_line.product_uom_id._compute_quantity(order_line.qty, order_line.product_id.uom_id)
        return float_compare(available_qty, scrap_qty, precision_digits=precision) >= 0

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ['same_line_id','cashier_id','barcode']
        return params


    def _prepare_move_values(self,scrap):
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

    def do_scrap(self,order_line):
        scrap_id = self.env['stock.scrap'].create({
            'product_id': order_line.product_id.id,
            'product_uom_id': order_line.product_uom_id.id,
            'scrap_qty': order_line.qty,
            'location_id': self._get_default_location_id(),
            'scrap_location_id': self._get_default_scrap_location_id(),
            'extra_note': self.extra_note,
        })
        for scrap in scrap_id:
            scrap.name = self.env['ir.sequence'].next_by_code('stock.scrap') or _('New')
            move = self.env['stock.move'].create(self._prepare_move_values(scrap))
            move.with_context(is_scrap=True)._action_done()
            scrap.write({'state': 'done'})
            scrap.date_done = fields.Datetime.now()
            order_line.is_scraped = True
            order_line.scrap_id = scrap.id
        return True

    def create_scrap_from_pos(self,order,order_line):
        order_line = self.env['pos.order.line'].browse(order_line)
        if float_is_zero(order_line.qty,
                         precision_rounding=order_line.product_uom_id.rounding):
            raise UserError(_('You can only enter positive quantities.'))

        if self.check_available_qty(order_line):
            return self.do_scrap(order_line)
        else:
            raise UserError(_('Not Scraped'))
