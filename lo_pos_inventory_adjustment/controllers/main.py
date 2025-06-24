
import odoo
from odoo import http
from odoo.http import request
import odoo.exceptions
from odoo import api, fields, models, _


class PosInventoryAdjust(http.Controller):

    @http.route("/check_location", auth="user", type="json")
    def check_location(self, location_barcode, **kw):
        if location_barcode:
            location_id = request.env['stock.location'].sudo().search([('barcode', '=', str(location_barcode))])
            if location_id:
                return True
        return False

    @http.route("/create/inventory_from_pos", auth="user", type="json")
    def create_inventory_from_pos(self, header, orders, validate):
        val = []
        is_true = False
        for values in orders.get('line_ids'):
            product_id = request.env['product.product'].sudo().browse(values[2]['product_id'])
            if product_id and not product_id.is_storable and not product_id.type != 'consu':
                is_true = True
                msgSC = _("You can only adjust storable products. \n%s -> %s") % (product_id.display_name, product_id.type)
                val.append(msgSC)
            else:
                session_id = request.env['pos.config'].sudo().browse(int(header[0]['pos_config_id']))
                if session_id.is_multi_location:
                    location_id = request.env['stock.location'].sudo().search([('barcode', '=', str(header[0]['location_no']))])
                else:
                    location_id = request.env['stock.location'].sudo().browse(values[2]['location_id'])

                quant_id = request.env['stock.quant'].sudo().search(
                    [('location_id', '=', location_id.id), ('product_id', '=', product_id.id),
                     ('lot_id', '=', False)], limit=1)

                if quant_id:
                    quant_id.user_id = request.env.user.id
                    quant_id.inventory_quantity_set = True
                    quant_id.pos_name = header[0]['pos_name']
                    quant_id.employee_id = int(header[0]['employee_id'])
                    quant_id.warehouse_no = header[0]['warehouse_no']
                    quant_id.location_no = header[0]['location_no']
                    quant_id.pda = header[0]['pda']
                    quant_id.date_ending = fields.datetime.now()

                    if quant_id.inventory_quantity == 0.0:
                        quant_id.inventory_quantity = float(values[2]['product_qty'])
                    else:
                        quant_id.inventory_quantity = quant_id.inventory_quantity + float(values[2]['product_qty'])
                    if validate:
                        quant_id.action_apply_inventory()
                else:
                    quant_value = {
                        'product_id': product_id.id,
                        'location_id': location_id.id,
                        'inventory_quantity': float(values[2]['product_qty']),
                        'user_id': request.env.user.id,
                        'date_ending': fields.datetime.now(),
                        'inventory_quantity_set': True,
                        'pos_name': header[0]['pos_name'],
                        'employee_id': int(header[0]['employee_id']),
                        'warehouse_no': header[0]['warehouse_no'],
                        'location_no': header[0]['location_no'],
                        'pda': header[0]['pda'],
                    }

                    quant_id = request.env['stock.quant'].sudo().create(quant_value)
                    if validate:
                        quant_id.action_apply_inventory()

                stock_counted_id = request.env['stock.count.adjust'].sudo().create({
                    'counted_date': fields.datetime.now(),
                    'stock_quant_id': quant_id.id,
                    'product_id': product_id.id,
                    'location_id': location_id.id,
                    'qty_onhand': quant_id.quantity,
                    'counted_qty': float(values[2]['product_qty']),
                    'user_id': request.env.user.id,
                    'pos_name': header[0]['pos_name'],
                    'employee_id': int(header[0]['employee_id']),
                    'warehouse_no': header[0]['warehouse_no'],
                    'location_no': header[0]['location_no'],
                    'pda': header[0]['pda'],
                })

        if is_true:
            return val
