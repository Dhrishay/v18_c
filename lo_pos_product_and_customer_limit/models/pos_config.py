# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import convert, SQL


class PosConfig(models.Model):
    _inherit = 'pos.config'

    limited_products_loading = fields.Boolean(string='Limited Product Loading',
                                              help="we load all starred products (favorite).\n"
                                                   "When the session is open, we keep on loading all remaining products in the background.\n",default=False)
    limited_product_count = fields.Integer(string="Number of Products Loaded",default=20000)
    product_load_background = fields.Boolean(default=False)


    limited_partners_loading = fields.Boolean('Limited Partners Loading',
                                              help="By default, 10000 Customers are loaded.\n"
                                                   "When the session is open, we keep on loading all remaining Customers in the background.\n",default=False)
    limited_partner_count = fields.Integer(string="Number of Customers Loaded",default=10000)
    partner_load_background = fields.Boolean(default=False)

    def get_limited_product_count(self):
        print("\n\n\nget_limited_product_count-----------------------------------")
        default_limit = 20000
        config_param = self.limited_product_count if self.limited_products_loading and self.limited_product_count > 0 else default_limit
        # print("config_param-------------------------------",config_param)
        try:
            return int(config_param)
        except (TypeError, ValueError, OverflowError):
            return default_limit

    def get_limited_partners_loading(self):
        print("\n\n\nget_limited_partners_loading--------------------------------------")
        default_limit = 10000
        limited_partner_count = self.limited_partner_count if self.limited_partners_loading and self.limited_partner_count > 0 else default_limit
        # print("limited_partner_count--------------------------------------",limited_partner_count)
        return self.env.execute_query(SQL("""
            WITH pm AS
            (SELECT   partner_id,
            Count(partner_id) order_count
            FROM pos_order GROUP BY partner_id)
            SELECT id
            FROM res_partner AS partner
            LEFT JOIN pm
            ON (partner.id = pm.partner_id)
            WHERE (partner.company_id=%s OR partner.company_id IS NULL)
            ORDER BY  COALESCE(pm.order_count, 0) DESC,NAME limit %s;
        """, self.company_id.id, limited_partner_count))

    def get_products_loading_in_background(self, fields, offset, limit):
        print("\n\n\nget_products_loading_in_background----------------------------------------")
        query = self.env['product.product']._where_calc(
            self._get_available_product_domain()
        )
        # print("query---------------------------------",query)
        sql = SQL(
            """
            WITH pm AS (
                  SELECT product_id,
                         MAX(write_date) date
                    FROM stock_move_line
                GROUP BY product_id
            )
               SELECT product_product.id
                 FROM %s
            LEFT JOIN pm ON product_product.id=pm.product_id
                WHERE %s
             ORDER BY product_product__product_tmpl_id.is_favorite DESC,
                      CASE WHEN product_product__product_tmpl_id.type = 'service' THEN 1 ELSE 0 END DESC,
                      pm.date DESC NULLS LAST,
                      product_product.write_date DESC
                LIMIT %s
               OFFSET %s
            """,
            query.from_clause,
            query.where_clause or SQL("TRUE"),
            int(limit),
            int(offset),  # Added offset parameter here
        )
        product_ids = [r[0] for r in self.env.execute_query(sql)]
        # print("product_ids--------------------------------",product_ids)
        special_products = self._get_special_products().filtered(
            lambda product: not product.sudo().company_id
                            or product.sudo().company_id == self.company_id
        )
        # product_ids.extend(special_products.ids)
        products = self.env['product.product'].browse(product_ids)
        # print("products----------------------------",products)
        product_combo = products.filtered(lambda p: p['type'] == 'combo')
        # print("product_combo-----------------------------",product_combo)
        product_in_combo = product_combo.combo_ids.combo_item_ids.product_id
        # print("product_in_combo-----------------------------",product_in_combo)
        products_available = products | product_in_combo
        # print("products_available-----------------------------",products_available)
        return products_available.read(fields, load=False)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    limited_products_loading = fields.Boolean(string="Limited Product Loading",related="pos_config_id.limited_products_loading",readonly=False)
    limited_product_count = fields.Integer(string="Number of Products Loaded",related="pos_config_id.limited_product_count",readonly=False)
    limited_partners_loading = fields.Boolean(string="Limited Customers Loading",related="pos_config_id.limited_partners_loading",readonly=False)
    limited_partner_count = fields.Integer(string="Number of Customers Loaded",related="pos_config_id.limited_partner_count",readonly=False)
    product_load_background = fields.Boolean(related="pos_config_id.product_load_background",readonly=False)
    partner_load_background = fields.Boolean(related="pos_config_id.partner_load_background",readonly=False)