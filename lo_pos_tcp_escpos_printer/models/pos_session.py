# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Laoodoo
# See LICENSE file for full copyright and licensing details.

from odoo import models, api
import json

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_pos_printer(self):
        result = super()._loader_params_pos_printer()
        result['search_params']['fields'].append(
            ['escpos_printer_ip', 'espos_printer_port', 'receipt_design', 'receipt_design_text', 'sticker_printer', 'escpos_print_cashdrawer'])
        return result

    @api.model
    def _load_pos_data_models(self, config_id):
        data = super()._load_pos_data_models(config_id)
        data += ['receipt.design.custom']
        return data
    

    #override
    @api.model
    def _set_last_order_preparation_change(self, order_ids):
        for order_id in order_ids:
            order = self.env['pos.order'].browse(order_id)
            last_order_preparation_change = {
                'lines': {},
                'generalNote': '',
            }
            for orderline in order['lines']:
                last_order_preparation_change['lines'][orderline.uuid + " - "] = {
                    "uuid": orderline.uuid,
                    "name": orderline.full_product_name,
                    "note": "",
                    "sticker_note": "",
                    "product_id": orderline.product_id.id,
                    "quantity": orderline.qty,
                    "attribute_value_ids": orderline.attribute_value_ids.ids,
                }
            order.write({'last_order_preparation_change': json.dumps(last_order_preparation_change)})
