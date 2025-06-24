from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, get_lang
from odoo.tools.float_utils import float_round


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model_create_multi
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        for rec in res:
            if rec.picking_type_id.code =='outgoing':
                rec.name = self.env['ir.sequence'].next_by_code(
                    rec.company_id.sequence_deliver_order_id.code
                )
        return res


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    partner_id = fields.Many2one(
        'res.partner',
        default=lambda self: self.env.company.vendor_id.id if self.env.company.vendor_id else None,
        string='Partner'
    )
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
        default=lambda self: self.partner_id.property_purchase_currency_id.id)
    request_type = fields.Boolean(string='Request Type',default=False)
    is_without_price = fields.Boolean(string='Without Price',default=False)
    is_retutned = fields.Boolean(copy=False)
    return_request_type = fields.Boolean(string='Return Request Type',default=False)
    return_order_ids = fields.One2many("sale.order", "auto_purchase_order_id")
    return_id_count = fields.Integer(string="Sales", compute="_compute_return_order_ids")

    def _prepare_invoice(self):
        res = super(PurchaseOrder, self)._prepare_invoice()
        res['request_type'] = self.request_type
        return res

    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get('default_request_type', False):
            for vals in vals_list:
                company_id = self.env.company
                vals['name'] = self.env['ir.sequence'].next_by_code(company_id.sequence_ro_id.code) if company_id.sequence_ro_id.code else '/'
        return super(PurchaseOrder, self).create(vals_list)

    def button_confirm(self):
        if self.request_type:
            self = self.with_context(default_request_type=True, request_company_id=self.company_id.id)
        res = super(PurchaseOrder, self).button_confirm()
        return res

    @api.onchange('is_without_price')
    def onchange_is_without_price(self):
        if self.is_without_price:
            for l in self.order_line:
                l.price_unit = 0.00

    @api.depends('return_order_ids')
    def _compute_return_order_ids(self):
        for rec in self:
            return_order_ids = rec._get_sale_order_ids()
            rec.return_id_count = len(return_order_ids or [])

    def _get_sale_order_ids(self):
        sale_orders = self.env["sale.order"].search(
            [('auto_purchase_order_id', '=', self.id),('return_request_type','=',True), ('company_id', '=', self.company_id.id)]
        )
        return sale_orders.ids

    def action_view_return_sales(self):
        action = {
            "name": _("Sale Orders"),
            "res_model": "sale.order",
            "type": "ir.actions.act_window",
            "views": [[self.env.ref('sale.view_quotation_tree_with_onboarding').id, 'list'],[self.env.ref('lod_request_product_to_dc.delivery_order_form').id, "form"]],
            "context": {'default_return_request_type': True, "default_request_type": True,},
            "domain": [("id", "in", self._get_sale_order_ids()), ('return_request_type', '=', True), ('request_type', '=', True)],
        }
        return action

    def _prepare_picking(self):
        res = super()._prepare_picking()
        if self.return_request_type:
            res['return_request_type'] = True
        return res

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        today_date = fields.Datetime.now()  # Get today's date
        days = self.partner_id.lead_time
        if days > 0:
            self.date_planned = today_date + timedelta(days=days)
            self.date_order = today_date + timedelta(days=days + 7)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    qty_retutned = fields.Float("Retutned", compute="_compute_qty_retutned",readonly=False, copy=False)
    is_change_price = fields.Boolean(default=False)

    @api.depends('order_id.return_order_ids')
    def _compute_qty_retutned(self):
        for rec in self:
            total = 0.0
            for line in rec.order_id.return_order_ids.filtered(lambda sale: sale.state != 'cancel').order_line:
                total += line.product_uom_qty
            rec.qty_retutned = total
            if total == 0.0:
                rec.order_id.is_retutned = False

    @api.onchange('product_id')
    def _onchange_is_change_price(self):
        if self.order_id.is_without_price:
            self.is_change_price = True

    @api.depends('product_qty', 'product_uom', 'company_id', 'order_id.partner_id')
    def _compute_price_unit_and_date_planned_and_name(self):
        for line in self:
            if not line.product_id or line.invoice_lines or not line.company_id:
                continue
            params = line._get_select_sellers_params()
            seller = line.product_id._select_seller(
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order and line.order_id.date_order.date() or fields.Date.context_today(line),
                uom_id=line.product_uom,
                params=params)

            if line.order_id.partner_id and line.order_id.partner_id.lead_time:
                today_date = fields.Datetime.now() 
                days = line.order_id.partner_id.lead_time
                if not line.order_id.date_planned:
                   line.date_planned = today_date + timedelta(days=days)
                else:
                    line.date_planned = line.order_id.date_planned
            else:
                if seller or not line.date_planned:
                    line.date_planned = line._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

            # If not seller, use the standard price. It needs a proper currency conversion.
            if not seller:
                line.discount = 0
                unavailable_seller = line.product_id.seller_ids.filtered(
                    lambda s: s.partner_id == line.order_id.partner_id)
                if not unavailable_seller and line.price_unit and line.product_uom == line._origin.product_uom:
                    # Avoid to modify the price unit if there is no price list for this partner and
                    # the line has already one to avoid to override unit price set manually.
                    continue
                po_line_uom = line.product_uom or line.product_id.uom_po_id
                price_unit = line.env['account.tax']._fix_tax_included_price_company(
                    line.product_id.uom_id._compute_price(line.product_id.standard_price, po_line_uom),
                    line.product_id.supplier_taxes_id,
                    line.taxes_id,
                    line.company_id,
                )
                price_unit = line.product_id.cost_currency_id._convert(
                    price_unit,
                    line.currency_id,
                    line.company_id,
                    line.date_order or fields.Date.context_today(line),
                    False
                )
                price_unit = 0.0 if line.is_change_price else price_unit
                line.price_unit = float_round(
                    price_unit, precision_digits=max(
                        line.currency_id.decimal_places, self.env['decimal.precision'].precision_get('Product Price')
                    )
                )

            elif seller:
                price_unit = line.env['account.tax']._fix_tax_included_price_company(
                    seller.price, line.product_id.supplier_taxes_id,
                    line.taxes_id, line.company_id
                ) if seller else 0.0
                price_unit = seller.currency_id._convert(
                    price_unit, line.currency_id,
                    line.company_id,
                    line.date_order or fields.Date.context_today(line), False
                )
                price_unit = float_round(
                    price_unit, precision_digits=max(
                        line.currency_id.decimal_places, self.env['decimal.precision'].precision_get('Product Price')
                    )
                )
                price_unit = 0.0 if line.is_change_price else price_unit
                line.price_unit = seller.product_uom._compute_price(
                    price_unit, line.product_uom
                )
                line.discount = seller.discount or 0.0

            # record product names to avoid resetting custom descriptions
            default_names = []
            vendors = line.product_id._prepare_sellers(params=params)
            product_ctx = {
                'seller_id': None,
                'partner_id': None,
                'lang': get_lang(line.env, line.partner_id.lang).code
            }
            default_names.append(
                line._get_product_purchase_description(
                    line.product_id.with_context(product_ctx)
                )
            )
            for vendor in vendors:
                product_ctx = {
                    'seller_id': vendor.id,
                    'lang': get_lang(line.env, line.partner_id.lang).code
                }
                default_names.append(
                    line._get_product_purchase_description(
                        line.product_id.with_context(product_ctx)
                    )
                )
            if not line.name or line.name in default_names:
                product_ctx = {
                    'seller_id': seller.id,
                    'lang': get_lang(line.env, line.partner_id.lang).code
                }
                line.name = line._get_product_purchase_description(
                    line.product_id.with_context(product_ctx)
                )
