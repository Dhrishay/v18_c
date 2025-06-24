# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Laoodoo
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    escpos_print = fields.Boolean(compute='_compute_escpos_print', store=True, readonly=False)
    escpos_printer_ip = fields.Char(compute='_compute_escpos_printer_ip', store=True, readonly=False)
    escpos_print_cashdrawer = fields.Boolean(compute='_compute_escpos_print_cashdrawer', store=True, readonly=False)
    espos_printer_port = fields.Integer(compute='_compute_espos_printer_port', store=True, readonly=False)

    order_receipt_type = fields.Selection(
        [('all', 'All'), ('menu_order_qty', 'Separate By Qty'), ('menu_order_product', 'Separate By Product')],
        compute='_compute_order_receipt_type', store=True, readonly=False)
    receipt_design = fields.Many2one('receipt.design.custom', string="Receipt Design",
                                     compute='_compute_receipt_design', store=True, readonly=False)
    receipt_design_text = fields.Text(string='Receipt Design Text', compute='_compute_receipt_design_text', store=True,
                                      readonly=False)
    sticker_printer = fields.Boolean(string="Sticker Printer")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.pos_config_id.write({
            'escpos_print': self.escpos_print or False,
            'escpos_printer_ip': self.escpos_printer_ip or '',
            'espos_printer_port': self.espos_printer_port or 9100,
            'escpos_print_cashdrawer': self.escpos_print_cashdrawer or False,
            'receipt_design': self.receipt_design or False,
            'receipt_design_text': self.receipt_design_text or False,
            'sticker_printer': self.sticker_printer or False,
            'escpos_print_cashdrawer': self.escpos_print_cashdrawer or False,
        })

    @api.depends('pos_config_id')
    def _compute_escpos_print(self):
        for res_config in self:
            res_config.escpos_print = res_config.pos_config_id.escpos_print

    @api.depends('pos_config_id')
    def _compute_escpos_printer_ip(self):
        for res_config in self:
            res_config.escpos_printer_ip = res_config.pos_config_id.escpos_printer_ip

    @api.depends('pos_config_id')
    def _compute_espos_printer_port(self):
        for res_config in self:
            res_config.espos_printer_port = res_config.pos_config_id.espos_printer_port

    @api.depends('pos_config_id')
    def _compute_escpos_print_cashdrawer(self):
        for res_config in self:
            res_config.escpos_print_cashdrawer = res_config.pos_config_id.escpos_print_cashdrawer

    @api.depends('pos_config_id')
    def _compute_order_receipt_type(self):
        for res_config in self:
            res_config.order_receipt_type = res_config.pos_config_id.order_receipt_type

    @api.depends('pos_config_id')
    def _compute_order_receipt_type(self):
        for res_config in self:
            res_config.sticker_printer = res_config.pos_config_id.sticker_printer

    @api.depends('pos_config_id')
    def _compute_receipt_design(self):
        for res_config in self:
            res_config.receipt_design = res_config.pos_config_id.receipt_design

    @api.depends('pos_config_id')
    def _compute_receipt_design_text(self):
        for res_config in self:
            res_config.receipt_design_text = res_config.pos_config_id.receipt_design_text

    @api.onchange('receipt_design')
    def _onchange_receipt_design(self):
        for rec in self:
            if rec.receipt_design:
                rec.receipt_design_text = rec.receipt_design.receipt_design_text
            else:
                rec.receipt_design_text = False
