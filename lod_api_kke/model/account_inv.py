# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
# from urllib3.exceptions import InsecureRequestWarning
# from urllib3 import disable_warnings
from odoo.http import Controller, Response, request, route
import requests
import json
import logging
_logger = logging.getLogger(__name__)
from markupsafe import Markup

class AccountMoveInherit(models.Model):
    _inherit = "account.move"
    
    # kke_url = 'https://dev.api.logi.kokkok.asia/odoo/v1.0/invoices' #test
    # api_key = '0cce233dc83551de30a37dfc1f8d44b73bce106c1a9e7f255c185b9d655b39f5' # test
    # kke_url = 'https://api.logi.kokkok.asia/odoo/v1.0/invoices' #product
    # api_key = '952d049c339ad042dbedd41947934183592ca6dcaa01b53a94dde436b8ae950a' #product
    
    def action_post(self, force=False):
        res = super(AccountMoveInherit, self).action_post()
        if self.sale_order_id:
            count_order = len(self.invoice_line_ids)
            if count_order > 0:
                if self.move_type == 'out_invoice' and self.sale_order_id.kke_delivery_type_id.code != '99':
                    self.prepare_date()
        return res

    def prepare_date(self):
        kke_url = self.env['ir.config_parameter'].sudo().get_param('lod_api_kke.kke_url')
        kke_api_key = self.env['ir.config_parameter'].sudo().get_param('lod_api_kke.kke_api_key')

        if kke_url and kke_api_key:
            headers = {'Content-Type': 'application/json','X-api-key': kke_api_key}
            data = self.data_dicts()
            json_string = json.dumps(data, indent=2)
            self.send_data_request('POST', kke_url, data, headers)
        else:
            self.set_message_post('Send to KKE',(f'<span style="color: blue;"> Url and API key not be empty </span>'))
            
    def data_dicts(self):
        stock_picking_id = request.env['stock.picking'].sudo().search([('origin','=',self.sale_order_id.name),('picking_type_code','=','outgoing'), ('state','!=','cancel')], limit=1)
        
        city = stock_picking_id.location_id.warehouse_id.partner_id.city
        city = city if city else ""
        
        state_id = stock_picking_id.location_id.warehouse_id.partner_id.state_id.name
        state_id = state_id if state_id else ""
        
        country = stock_picking_id.location_id.warehouse_id.partner_id.country_id.name
        country = country if country else ""
        
        pick_up_address = f"{city} {state_id} {country}"
            
        pickup_phone_number =""
        if stock_picking_id.location_id.warehouse_id.partner_id.phone:
            pickup_phone_number = stock_picking_id.location_id.warehouse_id.partner_id.phone
        elif stock_picking_id.location_id.warehouse_id.partner_id.mobile:
            pickup_phone_number = stock_picking_id.location_id.warehouse_id.partner_id.mobile
        else:
            pickup_phone_number = ""
        
        dropoff_phone_number =""
        if self.partner_id.phone:
            dropoff_phone_number = self.partner_id.phone
        elif self.partner_id.mobile:
            dropoff_phone_number = self.partner_id.mobile
        else:
            dropoff_phone_number = ""

        items = []
        for invoice_line in self.invoice_line_ids:
            product_barcode = invoice_line.product_id.barcode if invoice_line.product_id and invoice_line.product_id.barcode else False
            if not product_barcode and invoice_line.product_id and invoice_line.product_id.barcode_ids:
                for barcode_id in invoice_line.product_id.barcode_ids:
                    product_barcode = barcode_id.name
                    break
            order_line = {
                "name": invoice_line.product_id.name if invoice_line.product_id.name else "",
                "amount": invoice_line.quantity,
                "unit": str(invoice_line.product_uom_id.name) if invoice_line.product_uom_id and invoice_line.product_uom_id.name else "",
                "price": invoice_line.price_subtotal,
                "barcode": product_barcode if product_barcode else "",
            }
            items.append(order_line)

        data =  {
            "no": self.name,
            "refNo": self.sale_order_id.name,
            "deliveryType": self.sale_order_id.kke_delivery_type_id.code if self.sale_order_id and self.sale_order_id.kke_delivery_type_id else "",
            "pickup": {
                "type": "cvs",
                "code": stock_picking_id.location_id.warehouse_id.view_location_id.name if stock_picking_id.location_id and stock_picking_id.location_id.warehouse_id and stock_picking_id.location_id.warehouse_id.view_location_id else "",
                "name": stock_picking_id.location_id.warehouse_id.name if stock_picking_id.location_id and stock_picking_id.location_id.warehouse_id else "",
                "address": pick_up_address,
                "coord": {
                    "x": stock_picking_id.location_id.warehouse_id.partner_id.partner_longitude if stock_picking_id.location_id.warehouse_id.partner_id.partner_longitude else 0.0,
                    "y": stock_picking_id.location_id.warehouse_id.partner_id.partner_latitude if stock_picking_id.location_id.warehouse_id.partner_id.partner_latitude else 0.0
                },
                "contactName": stock_picking_id.location_id.warehouse_id.partner_id.name if stock_picking_id.location_id and stock_picking_id.location_id.warehouse_id and stock_picking_id.location_id.warehouse_id.partner_id else "",
                "contactPhone": pickup_phone_number,
                "contactCountryCode": "856",
                "contactEmail": stock_picking_id.location_id.warehouse_id.partner_id.email if stock_picking_id.location_id and stock_picking_id.location_id.warehouse_id and stock_picking_id.location_id.warehouse_id.partner_id and stock_picking_id.location_id.warehouse_id.partner_id.email else ""
            },
            "dropoff": {
                "type": "cvs",
                "code": self.company_id.pc_code if self.company_id.pc_code else "",
                "name": self.company_id.name if self.company_id else "",
                "address": self.get_address_from_company() if self.company_id else "",
                "coord": {
                    "x": self.company_id.longitude if self.company_id and self.company_id.longitude else 0.0,
                    "y": self.company_id.latitude if  self.company_id and self.company_id.latitude else 0.0
                },
                "contactName": self.partner_id.name if self.partner_id and self.partner_id.name else "",
                "contactPhone": dropoff_phone_number,
                "contactCountryCode": "856",
                "contactEmail": self.partner_id.email if self.partner_id and self.partner_id.email else ""
            },
            "items" : items
        }
        return data


    def get_address_from_company(self):
        if self.sale_order_id and self.sale_order_id.company_id:
            comapny = self.sale_order_id.company_id
            parts = [x for x in [comapny.street, comapny.street2, comapny.city, comapny.state_id.name if comapny.state_id else None, comapny.country_id.name if comapny.country_id else None, comapny.zip] if x]
            return ", ".join(parts) + "." if parts else "."
        return ""

    def send_data_request(self, method, url, data, headers):
        desc=""
        response=""
        status_code=""
        color ="red"

        try:
            request_data = json.dumps(data)
            status_code = requests.request(method, url, data=request_data, headers=headers) 
            response = json.loads(status_code.text)
            
            if 'message' in response and response.get('message') == 'CREATED' and 'statusCode' in response and response.get('statusCode') == 201:
                color ="green"
                desc ='Request has been created Successfully! -> '+response.get('message')
            else:
                desc ='Request has been created failed! -> %s',response.get('message')
        except Exception as e:
            desc  = "Err exception: ",e
            response = f'{status_code} {response}, {desc}'
        finally:
            _logger.info('request####: %s', request_data)
            _logger.info('response:::: %s', response)
            _logger.info('description****: %s', desc)
            self.set_message_post('Send to KKE',(f'<span style="color:{color};">Response: {response} </span>'))
            
    def set_message_post(self, subject, body):
        self.message_post(
            body=Markup(_(body)),
            subject=subject,
            subtype_xmlid='mail.mt_note',
            author_id=request.env.user.partner_id.id
        )
        if self.sale_order_id:
            self.sale_order_id.message_post(
                body=Markup(_(body)),
                subject=subject,
                subtype_xmlid='mail.mt_note',
                author_id=request.env.user.partner_id.id
            )  