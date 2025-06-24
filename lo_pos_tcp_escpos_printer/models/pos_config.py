# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Laoodoo
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    escpos_printer_ip = fields.Char(string='Printer IP',
                                    help="Local IP address of an receipt printer.")
    espos_printer_port = fields.Integer(string='PORT', help="Printer Port", default=9100)
    escpos_print = fields.Boolean()
    escpos_print_cashdrawer = fields.Boolean()
    order_receipt_type = fields.Selection(
        [('all', 'All'), ('menu_order_qty', 'Separate By Qty'), ('menu_order_product', 'Separate By Product')],
        string='Receipt Type')
    receipt_design = fields.Many2one('receipt.design.custom', string='Receipt Design')
    receipt_design_text = fields.Text(string='Receipt Design Text')
    sticker_printer = fields.Boolean(string="Sticker Printer")

    @api.onchange('receipt_design')
    def _onchange_receipt_design(self):
        for rec in self:
            if rec.receipt_design:
                rec.receipt_design_text = rec.receipt_design.receipt_design_text
            else:
                rec.receipt_design_text = False
