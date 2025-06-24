# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, http
from odoo.exceptions import ValidationError
from odoo.osv import expression
from collections import defaultdict
from odoo.http import request, Response
from odoo.tools import float_compare, float_round
from odoo.addons.stock_barcode.controllers.stock_barcode import StockBarcodeController

class ProductStockBarcodeController(StockBarcodeController):

    @http.route()
    def get_specific_barcode_data(self, **kwargs):
        request.env.context = {**kwargs.get('context', {}), **request.env.context, 'display_default_code': False}
        barcodes_by_model = kwargs.get('barcodes_by_model')
        domains_by_model = kwargs.get('domains_by_model', {})
        universal_domain = domains_by_model.get('all')
        fetch_quant = kwargs.get('fetch_quants')
        nomenclature = request.env.company.nomenclature_id
        result = defaultdict(list)
        product_ids = set()

        if barcodes_by_model and barcodes_by_model.get('product.product') and not barcodes_by_model.get('stock.lot'):
            barcodes_by_model['stock.lot'] = []

        # If a barcode was given but no model was specified, search for it for all relevant models.
        if not barcodes_by_model:
            barcode_field_by_model = self._get_barcode_field_by_model()
            barcodes = kwargs.get('barcodes') or [kwargs.get('barcode')]
            barcodes_by_model = {model_name: barcodes for model_name in barcode_field_by_model.keys()}
        result['resticateMissingRecod'] = False
        for model_name, barcodes in barcodes_by_model.items():
            if not barcodes:
                continue
            barcode_field = request.env[model_name]._barcode_field
            domain = [(barcode_field, 'in', barcodes)]

            if nomenclature.is_gs1_nomenclature:
                # If we use GS1 nomenclature, the domain might need some adjustments.
                converted_barcodes_domain = []
                unconverted_barcodes = []
                for barcode in set(barcodes):
                    try:
                        # If barcode is digits only, cut off the padding to keep the original barcode only.
                        barcode = str(int(barcode))
                        if converted_barcodes_domain:
                            converted_barcodes_domain = expression.OR([
                                converted_barcodes_domain,
                                [(barcode_field, 'ilike', barcode)]
                            ])
                        else:
                            converted_barcodes_domain = [(barcode_field, 'ilike', barcode)]
                    except ValueError:
                        unconverted_barcodes.append(barcode)
                        pass  # Barcode isn't digits only.
                if converted_barcodes_domain:
                    domain = converted_barcodes_domain
                    if unconverted_barcodes:
                        domain = expression.OR([
                            domain,
                            [(barcode_field, 'in', unconverted_barcodes)]
                        ])
            # Adds additionnal domain if applicable.
            domain_for_this_model = domains_by_model.get(model_name)
            if domain_for_this_model:
                domain = expression.AND([domain, domain_for_this_model])
            if universal_domain:
                domain = expression.AND([domain, universal_domain])
            # Search for barcodes' records.
            records = request.env[model_name].search(domain)
            if not records:
                if model_name == 'product.product':
                    barcode_ids = request.env['product.barcode.multi'].sudo().search([('name', 'in', barcodes)])
                    if barcode_ids:
                        domain = [('barcode_ids', 'in', barcode_ids.ids)]
                        result['resticateMissingRecod'] = True
                        records = request.env[model_name].search(domain)

            fetched_data = self._get_records_fields_stock_barcode(records)
            if fetch_quant and model_name == 'product.product':
                product_ids = records.ids
            for f_model_name in fetched_data:
                result[f_model_name] = result[f_model_name] + fetched_data[f_model_name]

        if fetch_quant and product_ids:
            quants = request.env['stock.quant'].search([('product_id', 'in', product_ids)])
            fetched_data = self._get_records_fields_stock_barcode(quants)

            for f_model_name in fetched_data:
                result[f_model_name] = result[f_model_name] + fetched_data[f_model_name]
        product_id_list = []
        for rec in result.get('product.product'):
            if rec.get('id') in product_id_list:
                result.get('product.product').remove(rec)
            else:
                product_id_list.append(rec.get('id'))

        return result