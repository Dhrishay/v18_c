# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Laoodoo
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PosPrinter(models.Model):
    _inherit = 'pos.printer'

    printer_type = fields.Selection(selection_add=[('escpos_printer', 'Use an esc/pos printer')])
    escpos_printer_ip = fields.Char(string='Printer IP Address', help="Local IP address of an receipt printer.")
    espos_printer_port = fields.Integer(string='PORT', help="Printer Port", default=9100)

    order_receipt_type = fields.Selection(
        [('all', 'All'), ('menu_order_qty', 'Separate By Qty'), ('menu_order_product', 'Separate By Product')],
        string='Receipt Type', default='all')
    receipt_design = fields.Many2one('receipt.design.custom', string='Receipt Design', domain="['|', ('company_id', '=', company_id), ('company_id', '=', False)]")
    receipt_design_text = fields.Text(string='Receipt Design Text')
    sticker_printer = fields.Boolean(string="Sticker Printer")

    @api.onchange('receipt_design')
    def _onchange_receipt_design(self):
        for rec in self:
            if rec.receipt_design:
                rec.receipt_design_text = rec.receipt_design.receipt_design_text
            else:
                rec.receipt_design_text = False

    @api.constrains('escpos_printer_ip')
    def _constrains_escpos_printer_ip(self):
        for record in self:
            if record.printer_type == 'escpos_printer' and not record.escpos_printer_ip:
                raise ValidationError(_("Printer IP Address cannot be empty."))

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ['escpos_printer_ip', 'espos_printer_port', 'order_receipt_type', 'receipt_design',
                   'receipt_design_text', 'sticker_printer']
        return params
