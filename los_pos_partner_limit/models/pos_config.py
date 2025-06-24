from odoo import models, fields
from odoo.tools import convert, SQL


class PosConfig(models.Model):
     _inherit = 'pos.config'

     limited_partners_loading = fields.Boolean('Limited Partners Loading',
                                               help="By default, 10000 Customers are loaded.\n"
                                                    "When the session is open, we keep on loading all remaining Customers in the background.\n",
                                               default=False)
     limited_partner_count = fields.Integer(string="Number of Customers Loaded", default=10000)
     partner_load_background = fields.Boolean(default=False)

     def get_limited_partners_loading(self):
          print("\n\n\nget_limited_partners_loading--------------------------------------")
          default_limit = 10000
          limited_partner_count = self.limited_partner_count if self.limited_partners_loading and self.limited_partner_count > 0 else default_limit
          print("limited_partner_count--------------------------------------",limited_partner_count)
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

