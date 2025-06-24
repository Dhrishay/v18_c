# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
import calendar


class AssetModifyInherit(models.TransientModel):
    _inherit = 'asset.modify'

    partner_id = fields.Many2one('res.partner',string="Customer")
    product_id = fields.Many2one('product.product', string='Product')

    def sell_dispose(self):
        self.ensure_one()
        asset_id = self.env[self.env.context.get('active_model')].search([('id', '=', int(self.env.context.get('active_id')))])
        price = 0.0
        if asset_id.method_period == '1':
            input_date = datetime.strptime(str(self.date), "%Y-%m-%d").date()
            last_date_of_year = input_date.replace(month=12, day=31)
            last_day = calendar.monthrange(input_date.year, input_date.month)[1]
            last_date_of_month = input_date.replace(day=last_day)
            price = asset_id.depreciation_move_ids.filtered(lambda date: date.date == last_date_of_month).asset_remaining_value
        else:
            last_day_of_year = datetime.strptime(str(self.date), "%Y-%m-%d").replace(month=12, day=31).date()
            price = asset_id.depreciation_move_ids.filtered(lambda date: date.date == last_day_of_year).asset_remaining_value
        
        if self.partner_id:
            SaleOrder = self.env['sale.order']
            SaleOrderLine = self.env['sale.order.line']
            sale_order = SaleOrder.create({
                'partner_id': self.partner_id.id,
                'partner_id': self.partner_id.id,
                'client_order_ref': asset_id.name if asset_id else '',
                'date_order': self.date,
            })
            SaleOrderLine.create({
                'product_id': self.product_id.id, 
                'product_uom_qty': 1, 
                'price_unit': price,
                'order_id': sale_order.id,
            })
            sale_order.sudo().action_confirm()
            if sale_order.approval_level_id:
                sale_order.action_approve_order()
            picking = sale_order.picking_ids
            picking.update({'scheduled_date': self.date})
            lot = self.env['stock.lot'].search([('product_id', '=', self.product_id.id)], limit=1)
            for move_line in picking.move_ids_without_package:
                if move_line.quantity == 0.0:
                    move_line.update({'quantity': 1.0,'lot_ids': [(4, lot.id, 0)]})

            invoice = sale_order._create_invoices()
            invoice.update({'invoice_date': self.date, 'is_created_from_asset': True})
            invoice.action_post()
            invoice_line = invoice.invoice_line_ids
            self.sudo().write({
                'invoice_ids': [(6, 0, invoice.ids)],
                'invoice_line_ids': [(6, 0, invoice_line.ids)],
            })
            asset_id.sudo().write({
                'sale_order_ids': [(4, sale_order.id, 0)],
                'account_move_ids': [(4, invoice.id, 0)],
                'picking_ids': [(4, picking.id, 0)],
            })
        if self.gain_account_id == self.asset_id.account_depreciation_id or self.loss_account_id == self.asset_id.account_depreciation_id:
            raise UserError(_("You cannot select the same account as the Depreciation Account"))
        invoice_lines = self.env['account.move.line'] if self.modify_action == 'dispose' else self.invoice_line_ids
        return self.asset_id.set_to_close(invoice_line_ids=invoice_lines, date=self.date, message=self.name)