# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _ , tools
import random
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class POSConfigSummery(models.Model):
	_inherit = 'pos.config'
	
	order_summery = fields.Boolean('Order Summery')
	product_summery = fields.Boolean('Product Summery')
	product_categ_summery = fields.Boolean('Product Category Summery')
	loc_summery = fields.Boolean('Audit Report')
	payment_summery = fields.Boolean('Payment Summery')


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'


	order_summery = fields.Boolean(related='pos_config_id.order_summery',readonly=False)
	product_summery = fields.Boolean(related='pos_config_id.product_summery',readonly=False)
	product_categ_summery = fields.Boolean(related='pos_config_id.product_categ_summery',readonly=False)
	loc_summery = fields.Boolean(related='pos_config_id.loc_summery',readonly=False)
	payment_summery = fields.Boolean(related='pos_config_id.payment_summery',readonly=False)

class PosSession(models.Model):
	_inherit = 'pos.session'


	@api.model
	def _load_pos_data_models(self, config_id):
		result = super()._load_pos_data_models(config_id)
		result.extend(['stock.location'])
		return result

class stockLocation(models.Model):
	_inherit = 'stock.location'

	@api.model
	def _load_pos_data_domain(self, data):
		return [('company_id', '=', data['pos.config']['data'][0]['company_id'])]

	@api.model
	def _load_pos_data_fields(self, config_id):
		return []

	def _load_pos_data(self, data):
		domain = self._load_pos_data_domain(data)
		fields = self._load_pos_data_fields(data['pos.config']['data'][0]['id'])
		user = self.search_read(domain, fields, load=False)
		return {
			'data': user,
			'fields': fields,
		}


class PosOrderSummery(models.Model):
	_inherit = 'pos.order'

	location_id = fields.Many2one(comodel_name='stock.location',string="Location", store=True,compute="compute_location")
	
	@api.depends('picking_ids')
	def compute_location(self):
		for rec in self:
			rec.location_id = False
			for pck in rec.picking_ids:
				rec.location_id = pck.location_id

	def update_order_summery(self, ord_st_date, ord_end_date, ord_state,curr_session,order_current_session):
		to_day_date = datetime.now().date()		
		summery_order = []
		current_lang = self.env.context

		if order_current_session == True:
			if ord_state == 'Select State':
				orders = self.env['pos.order'].search([
					('session_id', '=', curr_session),
					('state', 'in', ['paid','invoiced','done']),
					])
			else:
				orders = self.env['pos.order'].search([
					('session_id', '=', curr_session),
					('state','=',ord_state.lower()),
					])

		else:
			if ord_state == 'Select State':
				orders = self.env['pos.order'].search([
					('date_order', '>=', ord_st_date + ' 00:00:00'),
					('date_order', '<=', ord_end_date + ' 23:59:59'),
					('state', 'in', ['paid','invoiced','done']),
					])
			else:
				orders = self.env['pos.order'].search([
					('date_order', '>=', ord_st_date + ' 00:00:00'),
					('date_order', '<=', ord_end_date + ' 23:59:59'),
					('state','=',ord_state.lower()),
					])
		for order in orders:
			date = order.date_order.strftime('%Y-%m-%d')
			summery_order.append({'name': order.name, 'total': order.amount_total, 'date':date, 'state':order.state})

		return summery_order
	
	def update_product_summery(self,pro_st_date,pro_ed_date,prod_current_session,curr_session):
		config_obj = self.env['pos.config'].search([])
		current_lang = self.env.context

		if prod_current_session:
			orders = self.env['pos.order'].search([
			('session_id', '=', curr_session),
			('state', 'in', ['paid','invoiced','done']),
			('config_id', 'in', config_obj.ids)])

		else:
			if pro_st_date and pro_ed_date :
				orders = self.env['pos.order'].search([
					('date_order', '>=', pro_st_date + ' 00:00:00'),
					('date_order', '<=', pro_ed_date + ' 23:59:59'),
					('state', 'in', ['paid','invoiced','done']),
					('config_id', 'in', config_obj.ids)])
			else:
				orders = self.env['pos.order'].search([
					('session_id', '=', curr_session),
					('state', 'in', ['paid','invoiced','done']),
					('config_id', 'in', config_obj.ids)])

		pos_line_ids = self.env["pos.order.line"].search([('order_id', 'in', orders.ids)]).ids
		
		
		if pos_line_ids:
			self.env.cr.execute("""
				SELECT product_tmpl.name, sum(pos_line.qty) total
				FROM pos_order_line AS pos_line,
					 pos_order AS pos_ord,
					 product_product AS product,
					 product_template AS product_tmpl
				WHERE pos_line.product_id = product.id
					AND product.product_tmpl_id = product_tmpl.id
					AND pos_line.order_id = pos_ord.id
					AND pos_line.id IN %s 
				GROUP BY product_tmpl.name
				
			""", (tuple(pos_line_ids),))
			products = self.env.cr.dictfetchall()
		else:
			products = []

		return products

class LocationSumm(models.Model):

	_name = "pos.order.location" 
	_description ="POS Order Locaton"

	
	def update_location_summery(self, location,select_session,tab1,tab2):
		res = []
		prod =[]
		prod_data ={}
		product_ids = self.env['product.product'].search([])
		if tab1 == True:
			session_id = self.env['pos.session'].browse(int(select_session))
			orders = self.env['pos.order'].search([
					('session_id', '=', session_id.id),
					('state', 'in', ['paid','invoiced','done']),
					])
			for odr in orders:
				for line in odr.lines:
					quants = self.env['stock.quant'].search([('product_id.id', '=', line.product_id.id),
						('location_id.id', '=', odr.location_id.id)])
					product = line.product_id.name
					if product in prod_data:
						old_qty = prod_data[product]['qty']
						prod_data[product].update({
						'qty' : old_qty+line.qty,
						})
					else:
						if len(quants) > 1:
							quantity = 0.0
							for quant in quants:
								quantity += quant.quantity

							prod_data.update({ product : {
								'product_id':line.product_id.id,
								'product_name':line.product_id.name,
								'qty' : line.qty,
								'avail_qty':quantity,
							}})
						else:
							prod_data.update({ product : {
								'product_id':line.product_id.id,
								'product_name':line.product_id.name,
								'qty' : line.qty,
								'avail_qty':quants.quantity,
							}})
		else:
			orders = self.env['pos.order'].search([('state', 'in', ['paid','invoiced','done']),])
			location_id = int(location)
			for odr in orders:
				if odr.location_id.id == location_id :
					for line in odr.lines:
						quants = self.env['stock.quant'].search([
							('product_id.id', '=', line.product_id.id),
							('location_id.id', '=', location_id)])

						product = line.product_id.name
						if product in prod_data:
							old_qty = prod_data[product]['qty']
							prod_data[product].update({
								'qty' : old_qty+line.qty,
							})
						else:
							if len(quants) > 1:
								quantity = 0.0
								for quant in quants:
									quantity += quant.quantity

								prod_data.update({ product : {
									'product_id':line.product_id.id,
									'product_name':line.product_id.name,
									'qty' : line.qty,
									'avail_qty':quantity,
								}})
							else:
								prod_data.update({ product : {
									'product_id':line.product_id.id,
									'product_name':line.product_id.name,
									'qty' : line.qty,
									'avail_qty':quants.quantity,
								}})

		return prod_data
		


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
