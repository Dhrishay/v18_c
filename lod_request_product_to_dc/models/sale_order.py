from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.addons.sale.models.sale_order_line import SaleOrderLine as ExtendSaleOrderLine

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    request_type = fields.Boolean(string='Request Type',default=False)
    return_request_type = fields.Boolean(string='Return Request Type',default=False,copy=False)
    is_without_price = fields.Boolean(string='Without Price',default=False)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(SaleOrder, self).create(vals_list)  
        if 'default_request_type' in self.env.context and self.env.context.get('default_request_type'):
            for record in res:  
                if record.company_id.sequence_rfdc_id:  
                   record.name =self.env['ir.sequence'].next_by_code(record.company_id.sequence_rfdc_id.code)
        return res
    
    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res['request_type'] = self.request_type
        return res

    def action_confirm(self):
        if self.request_type:
            self = self.with_context(default_request_type=True)
        res = super(SaleOrder, self).action_confirm()
        return res

    @api.onchange('is_without_price')
    def onchange_is_without_price(self):
        if self.is_without_price:
            for l in self.order_line:
                l.price_unit = 0.00

    def action_sale_ok(self): 
        res = super(SaleOrder,self).action_confirm() 
        delivery_group = self.env.ref("lod_request_product_to_dc.group_pick_stock", raise_if_not_found=False)
        if delivery_group:
            users = delivery_group.users
            for user in users:
                self.create_delivery_activity(user)
        return res

    def create_delivery_activity(self, user):
        for picking in self.picking_ids: 
            if picking.state not in ["done", "cancel"]:
                activity = self.env["mail.activity"].create({
                    "res_model_id": self.env["ir.model"]._get("stock.picking").id,  
                    "res_id": picking.id,  
                    "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,  
                    "summary": "Prepare Delivery",
                    "note": f"Please check and prepare the delivery for picking {picking.name}.",
                    "user_id": user.id,
                    "date_deadline": fields.Date.today(),
                })

    def _prepare_purchase_order_data(self, company, company_partner):
        res = super()._prepare_purchase_order_data(company, company_partner)
        res['return_request_type'] = True if self.return_request_type else False
        return res

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_change_price = fields.Boolean(default=False)
    
    @api.onchange('product_id')
    def _onchange_is_change_price(self):
        if self.order_id.is_without_price:
            self.is_change_price = True


@api.depends('product_id', 'product_uom', 'product_uom_qty')
def _compute_price_unit(self):
    for line in self:
        # Don't compute the price for deleted lines.
        if not line.order_id:
            continue
        # check if the price has been manually set or there is already invoiced amount.
        # if so, the price shouldn't change as it might have been manually edited.
        if (
            (line.technical_price_unit != line.price_unit and not line.env.context.get('force_price_recomputation'))
            or line.qty_invoiced > 0
            or (line.product_id.expense_policy == 'cost' and line.is_expense)
        ):
            continue
        line = line.with_context(sale_write_from_compute=True)
        if not line.product_uom or not line.product_id:
            line.price_unit = 0.0
            line.technical_price_unit = 0.0
        else:
            line = line.with_company(line.company_id)
            price = line._get_display_price()
            price = 0.0 if line.is_change_price else price
            line.price_unit = line.product_id._get_tax_included_unit_price_from_price(
                price,
                product_taxes=line.product_id.taxes_id.filtered(
                    lambda tax: tax.company_id == line.env.company
                ),
                fiscal_position=line.order_id.fiscal_position_id,
            )
            line.technical_price_unit = line.price_unit

ExtendSaleOrderLine._compute_price_unit = _compute_price_unit
