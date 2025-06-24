from odoo import models, fields, api


class SalePriceorDerLine(models.Model):
    _inherit = 'sale.order.line'

    cr_sale_price = fields.Float(string='Sale Price On Order')

    @api.model_create_multi
    def create(self, vals_list):
        res = super(SalePriceorDerLine, self).create(vals_list)
        for rec in res:
            for recor in rec.order_id.pricelist_id.item_ids:
                if recor.categ_id == rec.product_template_id.categ_id:
                    if recor.base == 'standard_price':
                        rec.price_unit = rec.product_template_id.standard_price - (
                                    recor.price_discount * rec.product_template_id.standard_price / 100)

            rec.cr_sale_price = rec.product_id.list_price
        return res

    def write(self, values):
        res = super(SalePriceorDerLine, self).write(values)
        if 'product_template_id' in values:
            for recor in self.order_id.pricelist_id.item_ids:
                if recor.categ_id == self.product_template_id.categ_id:
                    if recor.base == 'standard_price':
                        self.price_unit = self.product_template_id.standard_price - (
                                    recor.price_discount * self.product_template_id.standard_price / 100)

            self.cr_sale_price = self.product_template_id.list_price
        return res

    @api.onchange('product_template_id')
    def onchange_field_product_template_id(self):
        for rec in self:
            rec.cr_sale_price = rec.product_template_id.list_price


class SalePriceAccMoveLine(models.Model):
    _inherit = 'account.move.line'

    cr_sale_price = fields.Float(string='Sale Price On Order')

    @api.model_create_multi
    def create(self, vals_list):
        records = super(SalePriceAccMoveLine, self).create(vals_list)
        for record in records:
            record.cr_sale_price = record.sale_line_ids.cr_sale_price

        return records