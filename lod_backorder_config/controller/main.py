from odoo.addons.stock_barcode.controllers.stock_barcode import StockBarcodeController
from odoo import fields, http, _
from odoo.http import request


class BackorderStockBarcode(StockBarcodeController):

    @http.route('/stock_barcode/get_barcode_data', type='json', auth='user')
    def get_barcode_data(self, model, res_id):
        res = super().get_barcode_data(model, res_id)
        res['data']['config']['backorder_all_locations'] = request.env['stock.location'].search_read([
            ('company_id', '=', request.env.company.id)
        ], fields=['id', 'display_name'])
        res['data']['config']['backorder_location_id'] = request.env.company.backorder_location_id.id
        res['data']['config']['is_confirm_mapping'] = request.env.company.is_confirm_mapping
        res['data']['config']['backorder_location_name'] = request.env.company.backorder_location_id.display_name
        return res