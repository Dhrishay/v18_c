from odoo import http, fields, exceptions, _
from odoo.http import Controller, request, route

class WebsiteCheckPrice(http.Controller):

    def get_product_dict(self, stock_quant):
        return {
            'product_id': {
                'id': stock_quant.product_id.id if stock_quant.product_id else False,
                'display_name': stock_quant.product_id.display_name if stock_quant.product_id else False,
                'barcode': stock_quant.product_id.barcode if stock_quant.product_id else False,
                'has_image': bool(stock_quant.product_id.image_128)
            },
            'lot_id': {
                'id': stock_quant.lot_id.id,
                'name': stock_quant.lot_id.name,
            } if stock_quant.lot_id else False,
            'owner_id': {
                'id': stock_quant.owner_id.id,
                'display_name': stock_quant.owner_id.display_name,
            } if stock_quant.owner_id else False,
            'package_id': stock_quant.package_id.name if stock_quant.package_id else False,
            'quantity': stock_quant.quantity if stock_quant.quantity else False,
            'product_uom_id': stock_quant.product_uom_id.name if stock_quant.product_uom_id else False,
        }


    @http.route(['/check_location_and_product'], type='json',methods=['GET','POST'], auth="public")
    def check_location_and_product(self, barcode=None, **kwargs):
        values = {}
        if barcode != None:
            barcode_location_id = request.env['stock.location'].sudo().search([('barcode','=',barcode)], limit=1)
            user_type = request.env.user.has_group('lod_check_pro_loc_dc.group_stock_location_user')
            if barcode_location_id:
                location_stock_quants = []
                if user_type == True:
                    stock_quants = request.env['stock.quant'].sudo().search([('location_id.barcode', '=', barcode), ('location_id.usage', '=', 'internal')])
                else:
                    stock_quants = request.env['stock.quant'].sudo().search([('location_id.barcode', '=', barcode), ('location_id.usage', '=', 'internal'),('location_id', 'in', request.env.user.stock_location_ids.ids)])

                for q in stock_quants:
                    q_dict = self.get_product_dict(q)
                    location_stock_quants.append(q_dict)
                    values.update({
                        'is_location': True,
                        'is_product': False,
                        'location': barcode_location_id.display_name,
                        'location_stock_quants': location_stock_quants,
                    })
            else:
                if user_type == True:
                    stock_quants = request.env['stock.quant'].sudo().search([('location_id.barcode', '=', barcode), ('location_id.usage', '=', 'internal')])
                else:
                    stock_quants = request.env['stock.quant'].sudo().search([('location_id.barcode', '=', barcode), ('location_id.usage', '=', 'internal'),('location_id', 'in', request.env.user.stock_location_ids.ids)])

                location_ids = stock_quants.mapped('location_id')
                product_stock_quants = []
                if stock_quants:
                    if len(location_ids) > 1:
                        for location_id in location_ids:
                            barcode_ids = request.env['product.barcode.multi'].sudo().search([('name','=',barcode)])
                            product_id = False
                            if barcode_ids:
                                product_id = barcode_ids[0].product_id.id
                            location_stock = request.env['stock.quant'].sudo().search([('location_id.id','=',location_id.id),'|',('product_id.barcode', '=', barcode),('product_id','=',product_id)])
                            line_dict = {
                                'location_id' : {
                                    'id' : location_id.id,
                                    'name' : location_id.display_name
                                },
                                'product_ids' :  []
                            }
                            for q in location_stock:
                                prouct_dict = self.get_product_dict(q)
                                line_dict['product_ids'].append(prouct_dict)
                            product_stock_quants.append(line_dict)
                    elif len(location_ids) > 0:
                        location_id = location_ids[0]
                        barcode_ids = request.env['product.barcode.multi'].sudo().search([('name', '=', barcode)])
                        product_id = False
                        if barcode_ids:
                            product_id = barcode_ids[0].product_id.id
                        location_stock = request.env['stock.quant'].sudo().search([('location_id.id', '=', location_id.id),'|',('product_id.barcode', '=', barcode),('product_id', '=', product_id)])
                        line_dict = {
                            'location_id' : {
                                'id' : location_id.id,
                                'name' : location_id.display_name
                            },
                            'product_ids': []
                        }
                        for q in location_stock:
                            prouct_dict = self.get_product_dict(q)
                            line_dict['product_ids'].append(prouct_dict)
                        product_stock_quants.append(line_dict)
                    values.update({
                        'is_product': True,
                        'is_location': False,
                        'product_stock_quants': product_stock_quants,
                    })
                else:
                    values.update({
                        'is_product': False,
                        'is_location': False,
                    })
            return values
        else:
            values.update({
                'is_product': False,
                'is_location': False,
            })
            return values



    @http.route('/check_free_location', csrf=False, type='http', auth="public",  website=True)
    def check_free_location(self):
        values = {}
        user_type = request.env.user.has_group('lod_check_pro_loc_dc.group_stock_location_user')
        location = request.env.user.stock_location_ids.sudo().ids
        if user_type == True:
            location_ids = request.env['stock.location'].sudo().search([('quant_ids','=',False)])
        else:
            location_ids = request.env['stock.location'].sudo().search([('id','in',location),('quant_ids','=',False)])

        values.update({
            'location_ids': location_ids,
            'user_type': user_type,
        })
        action = request.env.ref('stock_barcode.stock_barcode_action_main_menu')
        if action:
            values['action'] = action.id
        return request.render("lod_check_pro_loc_dc.check_free_location_template", values)