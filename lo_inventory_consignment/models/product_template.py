from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_trade_term = fields.Selection(
        selection=[
            ('credit', 'Credit'),
            ('consignment', 'Consignment'),
            ('cash', 'Cash'),
        ],
        string='Type',
        tracking=True,
    )
    is_create_purchase_order_po = fields.Boolean(
        string='Create Purchase Order Pos'
    )

    @api.onchange('product_trade_term')
    def _onchange_product_trad_term(self):
        if self.product_trade_term == 'credit':
            self.is_storable = True
        else:
            self.is_storable = False
