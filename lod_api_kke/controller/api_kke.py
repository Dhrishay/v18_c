from odoo import http, fields
from odoo.http import request
import json
import datetime
import pytz
from odoo.http import Controller, Response, request, route
import requests
import base64
from odoo.tests import Form
import logging
from markupsafe import Markup
_logger = logging.getLogger(__name__)

class APIConnector(http.Controller):

    def check_access(self, header):

        # api_connect_id = request.env["rest.api"].sudo().search([], limit=1)
        # api_connect_id = request.env["rest.api"].sudo().search([('api_key','=', header.get("token-key"))], limit=1)
        # if api_connect_id:
        return {"message":"Success","status": True}
        # else:
        #     return {"message":"Invalid api key","status":False}
        
    @http.route( ["/api/update_status"], type="json", auth="none", methods=["POST"], website=True)
    def post_status(self):
        try:
            login_encoded = 'dGFsYWRsYW9AZ21haWwuY29t'      # cG9ydGFsdGVtcGxhdGVra2U=    #production
            pass_encoded = 'MTIz'
            login = self.str_decode(login_encoded)
            password = self.str_decode(pass_encoded)

            # credential = {'login': login, 'password': password, 'type': 'password'}
            credential = {'login': 'admin', 'password': 'admin', 'type': 'password'}

            request.session.authenticate(request.db, credential)
            header = request.httprequest.headers
            data = json.loads(request.httprequest.data)
            _logger.info('---------kkl request data--------->####: %s', data)  # 29/08/2024

            check_access = self.check_access(header)

            if check_access.get("status") == True:
                is_sucess = False
                msg = "Not found any stock picking"
                if data.get("delivery_status") in ("loading", "1"):
                    state = "loading"
                elif data.get("delivery_status") in ("on_transit", "2"):
                    state = "on_transit"
                elif data.get("delivery_status") in ("arrived", "3"):
                    state = "arrived"
                else:
                    return {"message": "Invalid Delivery status: "+ data.get("delivery_status"),"status": False}

                stock_picking_ids = ( request.env["stock.picking"].sudo().search([("origin", "=", data.get("order_no"))]))

                if stock_picking_ids:
                    if len(stock_picking_ids) > 0:
                        signatures=""
                        if state =='on_transit':
                            signatures = '''
                                <div class="container-fluid mt-2">
                                    <div class="row">
                                        <div class="col-sm-4">
                                        <h3>Pickup Contact</h3>
                                            <img src="pickup_contact_sign" style="height: 100px; width: 100px;"/>
                                        </div>
                                        <div class="col-sm-4">
                                        <h3>Pickup Freight</h3>
                                            <img src="pickup_freight" style="height: 100px; width: 100px;"/>
                                        </div>
                                        <div class="col-sm-4">
                                        <h3>Driver’s Signature</h3>
                                            <img src="driver_signature" style="height: 100px; width: 100px;"/>
                                        </div>
                                    </div>
                                </div>
                            '''
                            if 'contact_signature' in data:
                                signatures = signatures.replace('pickup_contact_sign',str(data.get("contact_signature")))
                            if 'freights' in data:
                                signatures = signatures.replace('pickup_freight',str(data.get("freights")[0]))
                            if 'driver_signature' in data:
                                signatures = signatures.replace('driver_signature',str(data.get("driver_signature")))
                            
                        if state =='arrived':
                            signatures = '''
                                <div class="container-fluid mt-2">
                                    <div class="row">
                                        <div class="col-sm-4">
                                        <h3>Dropoff Contact</h3>
                                            <img src="dropoff_contact_sign" style="height: 100px; width: 100px;"/>
                                        </div>
                                        <div class="col-sm-4">
                                        <h3>Dropoff Freight</h3>
                                            <img src="dropoff_freight" style="height: 100px; width: 100px;"/>
                                        </div>
                                    </div>
                                </div>
                                '''
                            if 'contact_signature' in data:
                                signatures = signatures.replace('dropoff_contact_sign',str(data.get("contact_signature")))
                            if 'freights' in data:
                                signatures = signatures.replace('dropoff_freight',str(data.get("freights")[0]))
                            
                        for stock_picking in stock_picking_ids:
                            # --------------------------------start 29/08/2024 ----------------------
                            # msg = f"your status is already '{stock_picking.delivery_state}' here!"
                            # if   stock_picking.picking_type_code in 'outgoing':
                            #     if stock_picking.delivery_state == 'loading' and state !='on_transit':
                            #         return {"message": "Next status must be on_transit", "status": False}
                                
                            #     if stock_picking.delivery_state == 'on_transit' and state !='arrived':
                            #         return {"message": "Next status must be arrived", "status": False}
                                
                            #     if stock_picking.delivery_state == 'arrived':
                            #         return {"message": "The process was finish.", "status": False}
                            # --------------------------------start 29/08/2024 ----------------------
                            
                            # if stock_picking.delivery_state != state:  # 29/08/2024
                            bodys = Markup(("KKE updated delivery state:  %s --> %s <br/> %s") % ( stock_picking.delivery_state,state,signatures))

                            try:
                                if state =='on_transit':
                                    color = "blue"
                                    stock_picking.sudo().write(
                                        {
                                            "delivery_state": state,
                                            "driver_name": data.get("driver_name") if 'driver_name' in data else '',
                                            "license_plate": data.get("license_plate") if 'license_plate' in data else '',
                                            "pickup_contact_sign": data.get("contact_signature") if 'contact_signature' in data else '',
                                            "pickup_freight": str(data.get("freights")) if 'freights' in data else '',
                                            "driver_signature": data.get("driver_signature") if 'driver_signature' in data else '',
                                            "kke_pick_time": fields.Datetime.now(), # 29/08/2024
                                        }
                                    )

                                    if stock_picking.picking_type_code == 'outgoing' and stock_picking.state != 'done':
                                        # stock_picking.sudo().button_validate()
                                        res_dict = stock_picking.sudo().button_validate()
                                        if res_dict != True:
                                            if res_dict.get('res_model') == 'stock.backorder.confirmation':
                                                wizard_backorder = Form(request.env['stock.backorder.confirmation'].sudo().with_context(res_dict['context'])).save()
                                                wizard_backorder.process_cancel_backorder()
                                            elif res_dict.get('res_model') == 'stock.immediate.transfer':
                                                wizard_apply_done = Form(request.env['stock.immediate.transfer'].sudo().with_context(res_dict['context'])).save().process()
                                                if wizard_apply_done == True:
                                                    pass
                                                elif wizard_apply_done.get('res_model') == 'stock.backorder.confirmation':
                                                    backorder = Form(request.env['stock.backorder.confirmation'].sudo().with_context(res_dict['context'])).save()
                                                    backorder.process_cancel_backorder()
                                    is_sucess = True

                                elif state =='arrived':
                                    color = "green"
                                    stock_picking.sudo().write(
                                        {
                                            "delivery_state": state,
                                            "driver_name": data.get("driver_name") if 'driver_name' in data else '',
                                            "license_plate": data.get("license_plate") if 'license_plate' in data else '',
                                            "dropoff_contact_sign": data.get("contact_signature") if 'contact_signature' in data else '',
                                            "dropoff_freight": str(data.get("freights")[0]) if 'freights' in data else '',
                                            "kke_drop_time": fields.Datetime.now(), # 29/08/2024
                                        }
                                    )
                                    is_sucess = True

                                stock_picking.message_post(body=bodys, subject="KKE update", subtype_xmlid="mail.mt_note", author_id = request.env.user.partner_id.id)
                            except Exception as e:
                                bodys = Markup(("<span style='color:red;'>KKE updated  state:  %s --> %s <br/> %s </span>") % ( stock_picking.delivery_state,state,str(e)))
                                stock_picking.message_post(body=bodys, subject="KKE update fail", subtype_xmlid="mail.mt_note", author_id = request.env.user.partner_id.id)
                    
                    if is_sucess:
                        post_message_log = (request.env["account.move"].sudo().search([("sale_order_id.name", "=", data.get("order_no"))], limit=1) )
                        if post_message_log:
                            post_message_log = post_message_log
                        else:
                            post_message_log = ( request.env["sale.order"].sudo().search([("name", "=", data.get("order_no"))], limit=1) )
                        bodys = Markup(f"<span style='color:{color};'>KKE on status:  {stock_picking.delivery_state}, Driver: {data.get('driver_name')}, Plate no: {data.get('license_plate')}</span>")
                        post_message_log.message_post(body=bodys, subject="KKE update", subtype_xmlid="mail.mt_note", author_id = request.env.user.partner_id.id)
                        return {"message": "Updated success status to : " + state,"status": True}
                    else:
                        return {"message": msg, "status": False}
                else:
                    return {"message": "Not found this order", "status": False}
            else:
                return {"message": "Not Success, Token-key invalid", "status": False}
        except Exception as e:
                _logger.info('Exceptin:======> %s',str(e)) # 29/08/2024
                return {'message': 'Exception: '+str(e), 'status': False}

    def str_encode(self, val):
        return base64.b64encode(val.encode()).decode()
    
    def str_decode(self, val):
        return base64.b64decode(val).decode()