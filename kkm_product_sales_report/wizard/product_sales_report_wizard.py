from odoo import api, fields, models
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ProducSalesReport(models.TransientModel):
    _name = 'sale.sumary.wizard'
    _description = 'Produc Sales Report (XLXS)'
    _rec_name = 'name'

    name = fields.Char('name', default='Commission Report')
    start_date = fields.Datetime(string='Date From', default=(datetime.now()+relativedelta(days=-1)).strftime('%Y-%m-%d 17:00:00'))
    end_date = fields.Datetime(string='Date To', default=(datetime.now()).strftime('%Y-%m-%d 16:59:59'))
    company_ids = fields.Many2many('res.company', string='Company')

    def action_xlsx(self):
        pos_order_line = self.env['pos.order.line']
        search_domain = [('create_date', '>=', self.start_date),('create_date', '<=', self.end_date),('order_id.company_id', 'in', self.company_ids.ids)]
        field = ['product_id','qty','price_subtotal_incl','total_cost']
        groupby_field = ['product_id']
        result = pos_order_line.read_group(search_domain,field, groupby_field)
        
        dict_data = {
            'header': ['Barcode', 'Product name', 'UOM', 'QTY','Cost','Sale Price','Actual sale','Total Cost','Product catagory'],
            'data': []
        }
        for product in result:
            get_product = self.env['product.product'].search([('id','=',product['product_id'][0]),('active','in',[False,True])])
            data = {
                'barcode': get_product.barcode,
                'product_name': get_product.name,
                'uom': get_product.uom_id.name,
                'qty': product['qty'],
                'cost': get_product.standard_price,
                'sale_price': get_product.list_price,
                'actual_sale': product['price_subtotal_incl'],
                'total_cost': product['total_cost'],
                'product_catagory': get_product.categ_id.complete_name,
                'product_id': product['product_id'][0],
            }
            dict_data['data'].append(data)
        data = {
            'form_data': self.read()[0],
            'data': dict_data
        }
        return self.env.ref('kkm_product_sales_report.action_report_action_sale_sumary').report_action(self, data=data)