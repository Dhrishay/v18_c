from odoo import models, api, fields, _
from datetime import date, timedelta


class PosOrder(models.Model):
    _inherit = 'pos.order'

    purchase_order_ids = fields.Many2many(
        'purchase.order',
        string='Linked Purchase Orders',
    )
    purchase_count = fields.Integer(compute='_compute_purchase_count')

    @api.model
    def cron_create_purchase_orders_for_mto_pos(self):
        today = date.today()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        pos_orders = self.search([
            ('date_order', '>=', first_day_of_month),
            ('date_order', '<=', last_day_of_month),
            ('state', 'in', ['paid', 'invoiced']),
            ('config_id.mto_purchase_order', '=', True)
        ])

        if not pos_orders:
            return

        config_groups = {}
        for order in pos_orders:
            config_id = order.config_id.id
            if config_id not in config_groups:
                config_groups[config_id] = self.env['pos.order']
            config_groups[config_id] |= order

        mto_route = self.env.ref('stock.route_warehouse0_mto').id
        buy_route = self.env.ref('purchase_stock.route_warehouse0_buy').id

        for config_id, orders in config_groups.items():
            for order in orders:
                vendor_lines_map = {}
                po_ids = []
                mto_lines = order.lines.filtered(
                    lambda l: l.product_id.product_trade_term == "consignment" and l.product_id.is_create_purchase_order_po
                )
                if not mto_lines:
                    continue

                for line in mto_lines:
                    vendor = order.company_id.parent_id.partner_id if order.company_id.parent_id else order.company_id.partner_id
                    if not vendor:
                        continue

                    if vendor not in vendor_lines_map:
                        vendor_lines_map[vendor] = {}

                    # Accumulate quantities and price for the same product
                    product_id = line.product_id.id
                    if product_id not in vendor_lines_map[vendor]:
                        # Calculate price with GP compensation
                        price = (vendor.gp_compensation_per / 100) * line.price_unit
                        price_unit = line.price_unit - price
                        vendor_lines_map[vendor][product_id] = {
                            'product': line.product_id,
                            'qty': 0,
                            'price_unit': price_unit,
                            'uom': line.product_id.uom_po_id,
                            'currency_id': order.currency_id.id,
                            'company_id': order.company_id.id,
                            'barcode': line.product_id.barcode,
                        }
                    vendor_lines_map[vendor][product_id]['qty'] += line.qty

                # Create a PO for each vendor
                for vendor, product_lines in vendor_lines_map.items():
                    if not product_lines:
                        continue

                    # Create a new PO for the vendor
                    po = self.env['purchase.order'].create({
                        'partner_id': vendor.id,
                        'origin': order.name,
                        'currency_id': order.currency_id.id,
                        'company_id': order.company_id.id,
                        'is_without_price': True,
                        'request_type': True,
                    })
                    po_ids.append(po.id) 

                    for product_data in product_lines.values():
                        self.env['purchase.order.line'].create({
                            'order_id': po.id,
                            'product_id': product_data['product'].id,
                            'name': product_data['product'].name,
                            'product_qty': product_data['qty'],
                            'product_uom': product_data['uom'].id,
                            'price_unit': product_data['price_unit'],
                            'date_planned': fields.Datetime.now(),
                            'barcode': product_data.get('barcode', ''),
                        })

                if po_ids:
                    for rec in po_ids:
                        po = self.env['purchase.order'].search([('id', '=', rec)])
                        po.onchange_is_without_price()
                        po.button_confirm()
                        sale_order = self.env['sale.order'].sudo().search([('client_order_ref','=', po.name), ('request_type', '=', True)])
                        sale_order.action_confirm()
                        for purchase in sale_order._get_purchase_orders():
                            purchase.sudo().button_confirm()
                    self.env['purchase.order'].flush_model()
                    order.sudo().write({
                        'purchase_order_ids': [(6, 0, po_ids)]
                    })

    @api.depends('purchase_order_ids')
    def _compute_purchase_count(self):
        for order in self:
            order.purchase_count = len(order.purchase_order_ids)

    def action_purchase_order(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_rfq')
        action['display_name'] = _('Purchase')
        action['context'] = {}
        action['domain'] = [('id', 'in', self.purchase_order_ids.ids)]
        return action
