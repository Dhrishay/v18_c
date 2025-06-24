# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.http import Controller, Response, request, route
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
import requests
import json
import operator 
import pandas as pd
import logging
_logger = logging.getLogger(__name__)
from markupsafe import Markup

class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    # kke_url = 'https://dev.api.logi.kokkok.asia/odoo/v1.0/invoices' #test
    # api_key = '0cce233dc83551de30a37dfc1f8d44b73bce106c1a9e7f255c185b9d655b39f5' # test
    # kke_url = 'https://api.logi.kokkok.asia/odoo/v1.0/invoices' #product
    # api_key = '952d049c339ad042dbedd41947934183592ca6dcaa01b53a94dde436b8ae950a' #product
    
    
    state = fields.Selection(
        selection_add=[
            ('loading', 'Loading'), 
            ('on_transit', 'On Transit'), 
            ('arrived', 'Arrived')
        ])
    
    delivery_state = fields.Selection(
        [
            ('loading', 'Loading'), 
            ('on_transit', 'On Transit'), 
            ('arrived', 'Arrived')
        ], default ='loading')
    driver_name = fields.Char('Driver Name')
    license_plate = fields.Char('License plate')
    
    pickup_contact_sign= fields.Char('Pickup Contact’s Signature')
    pickup_freight= fields.Char('Pickup Freight’s Signature')
    dropoff_contact_sign= fields.Char('Droppof Contact’s Signature')
    dropoff_freight= fields.Char('Dropoff Freight’s Signature')
    driver_signature = fields.Char('Driver’s signature')

    # <!-- start 29/08/2024 -->
    kke_pick_time = fields.Datetime(string='KKE Pick Time')
    kke_drop_time = fields.Datetime(string='KKE Drop Time')
    # <!-- end 29/08/2024 -->
    
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        if self.request_type and self.sale_id.kke_delivery_type_id.code != '99':
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
        city = self.location_id.warehouse_id.partner_id.city
        city = city if city else ""
        
        state_id = self.location_id.warehouse_id.partner_id.state_id.name
        state_id = state_id if state_id else ""
        
        country = self.location_id.warehouse_id.partner_id.country_id.name
        country = country if country else ""
        pick_up_address = f"{city} {state_id} {country}"

        pickup_phone_number =""
        if self.location_id.warehouse_id.partner_id.phone:
            pickup_phone_number = self.location_id.warehouse_id.partner_id.phone
        elif self.location_id.warehouse_id.partner_id.mobile:
            pickup_phone_number = self.location_id.warehouse_id.partner_id.mobile
        else:
            pickup_phone_number = ""

        dropoff_phone_number =""
        if self.sale_id.partner_id.phone:
            dropoff_phone_number = self.sale_id.partner_id.phone
        elif self.sale_id.partner_id.mobile:
            dropoff_phone_number = self.sale_id.partner_id.mobile
        else:
            dropoff_phone_number = ""

        items = []
        for move_line in self.move_line_ids_without_package:
            price = move_line.product_id.list_price
            if price:
                price = price
            elif move_line.product_id.standard_price:
                price = move_line.product_id.standard_price
            else:
                price = 0.0
            total_price = price * move_line.qty_done

            order_line = {
                "name": move_line.product_id.name if move_line.product_id.name else "",
                "amount": str(move_line.qty_done),
                "unit": str(move_line.product_uom_id.name) if move_line.product_uom_id.name else "",
                "price": total_price,
                "barcode": str(move_line.product_barcode) if move_line.product_barcode else "",
            }
            items.append(order_line)
        kke_total_cost = sum(m_line.qty_done * m_line.product_id.standard_price for m_line in
                             self.move_line_ids_without_package)  # <=======19/08/2024
        self.sale_id.kke_total_cost = kke_total_cost

        return {
            "no": self.name,
            "refNo": self.sale_id.name,
            "deliveryType": self.sale_id.kke_delivery_type_id.code if self.sale_id and self.sale_id.kke_delivery_type_id else "", # <============== 29/08/2024
            "pickup": {
                "type": "warehouse",
                "code": self.location_id.warehouse_id.view_location_id.name if self.location_id.warehouse_id.view_location_id.name else "",
                "name": self.location_id.warehouse_id.name if self.location_id.warehouse_id.name else "",
                "address": pick_up_address,
                "coord": {
                    "x": self.location_id.warehouse_id.partner_id.partner_longitude if self.location_id.warehouse_id.partner_id.partner_longitude else 0.0,
                    "y": self.location_id.warehouse_id.partner_id.partner_latitude if self.location_id.warehouse_id.partner_id.partner_latitude else 0.0
                },
                "contactName": self.location_id.warehouse_id.partner_id.name if self.location_id.warehouse_id.partner_id.name else "",
                "contactPhone": pickup_phone_number,
                "contactCountryCode": "856",
                "contactEmail": self.location_id.warehouse_id.partner_id.email if self.location_id.warehouse_id.partner_id.email else ""
            },
            "dropoff": {
                "type": "warehouse",
                "code": self.sale_id.company_id.pc_code if self.sale_id.company_id.pc_code else "",
                "name": self.sale_id.company_id.name if self.sale_id.company_id.name else "",
                "address": self.get_address_from_company() if self.sale_id.company_id else "",
                "coord": {
                    "x": self.sale_id.company_id.longitude if self.sale_id.company_id.longitude else 0.0,
                    "y": self.sale_id.company_id.latitude if self.sale_id.company_id.latitude else 0.0
                },
                "contactName": self.sale_id.partner_id.name if self.sale_id.partner_id.name else "",
                "contactPhone": dropoff_phone_number,
                "contactCountryCode": "856",
                "contactEmail": self.sale_id.partner_id.email if self.sale_id.partner_id.email else ""
            },
            "items":items
        }
                          
    def send_data_request(self, method, url, data, headers):
        desc=""
        response=""
        status_code=""
        color ="red"

        try:
            request_data = json.dumps(data)
            status_code = requests.request(method, url, data=request_data, headers=headers) 
            response = json.loads(status_code.text)
            
            if response.get('message') == 'CREATED' and response.get('statusCode') == 201:
                color ="green"
                desc ='Request has been created Successfully! -> '+response.get('message')
            else:
                desc ='Request has been created failed! -> %s',response.get('message')
        except Exception as e:
            desc  = "Err exception: ",e
            response = f'{status_code} {response}, Err exception: {e}'
        finally:
            _logger.info('request####: %s', request_data)
            _logger.info('response:::: %s', response)
            _logger.info('description****: %s', desc)
            self.set_message_post('Send to KKE',(f'<span style="color:{color};">Response: {response} </span>'))

    def get_address_from_company(self):
        if self.sale_id and self.sale_id.company_id:
            c = self.sale_id.company_id
            parts = [x for x in [c.street, c.street2, c.city, c.state_id.name if c.state_id else None, c.country_id.name if c.country_id else None, c.zip] if x]
            return ", ".join(parts) + "." if parts else "."
        return ""

    def set_message_post(self, subject, body):
        self.message_post(
            body=Markup(_(body)),
            subject=subject,
            subtype_xmlid='mail.mt_note',
            author_id=request.env.user.partner_id.id
        )
        if self.sale_id:
            self.sale_id.message_post(
                body=Markup(_(body)),
                subject=subject,
                subtype_xmlid='mail.mt_note',
                author_id=request.env.user.partner_id.id
            )

    def unlink(self):
        kke_url = self.env['ir.config_parameter'].sudo().get_param('lod_api_kke.kke_url')
        kke_api_key = self.env['ir.config_parameter'].sudo().get_param('lod_api_kke.kke_api_key')
         
        if kke_url and kke_api_key:
            headers = {'Content-Type': 'application/json','X-api-key': kke_api_key}
            for rec in self:
                data = {
                    "invoiceNo": rec.name,
                    "refNo": rec.sale_id.name if rec.sale_id else ""
                }
                desc = 'Record has been deleted failed!'
                try:
                    request_data = json.dumps(data)
                    status_code = requests.request('POST', kke_url, data=request_data, headers=headers)
                    response = json.loads(status_code.text)
                    _logger.info('request####: %s', request_data)
                    _logger.info('response:::: %s', response)
                    if response.get('message') == 'CREATED' and response.get('statusCode') == 201:
                        color = "green"
                        desc = 'Record has been deleted Successfully! -> ' + response.get('message')
                    else:
                        desc = 'Record has been deleted failed! -> %s', response.get('message')
                except Exception as e:
                    desc = e
                logger_message = desc
                if logger_message:
                    _logger.info(logger_message)
        res = super().unlink()
        return res