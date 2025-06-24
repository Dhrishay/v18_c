from odoo import models, fields
from odoo.tools import convert, SQL


class ResPartner(models.Model):
     _inherit = 'res.partner'

     def pos_load_data(self, pos_config_id=False, offset=0, limit=None):
          print("\n\n\npos_load_data-----------------partner----------------------")
          if pos_config_id:
               domain = self._load_pos_data_domain_offset(pos_config_id, offset, limit)
               fields = self._load_pos_data_fields(pos_config_id)
               return {'res.partner': {
                    'data': self.search_read(domain, fields, load=False),
                    'fields': self._load_pos_data_fields(pos_config_id),
               }
               }
          else:
               return False

     def _load_pos_data_domain_offset(self, pos_config_id, offset, limit):
          print("\n\n\n_load_pos_data_domain_offset------------------------------------")
          config_id = self.env['pos.config'].browse(pos_config_id)
          session_id = config_id.current_session_id
          data = {}
          company_id = session_id.company_id.id
          if session_id:
               data['pos.session'] = session_id._load_pos_data(data)
               res = session_id._load_pos_data_relations('pos.session', data)
               limited_partner_ids = {partner[0] for partner in self.get_limited_partners_loading_in_background(company_id, offset, limit)}
               limited_partner_ids.add(self.env.user.partner_id.id)
               domain = [('id', 'in', list(limited_partner_ids))]
               if 'pos.order' in data:
                    loaded_order_partner_ids = {order['partner_id'] for order in data['pos.order']['data']}
                    partner_ids = limited_partner_ids.union(loaded_order_partner_ids)
                    if partner_ids:
                         domain = [('id', 'in', list(partner_ids))]

               return domain

     def get_limited_partners_loading_in_background(self, company_id, offset, limit):
          print("\n\n\nget_limited_partners_loading_in_background-----------------------------")
          return self.env.execute_query(SQL("""
             WITH pm AS
             (SELECT partner_id,
             Count(partner_id) order_count
             FROM pos_order
             GROUP BY partner_id)
             SELECT id
             FROM res_partner AS partner
             LEFT JOIN pm
             ON (partner.id = pm.partner_id)
             WHERE (partner.company_id=%s OR partner.company_id IS NULL)
             ORDER BY  COALESCE(pm.order_count, 0) DESC, NAME limit %s OFFSET %s;""", company_id, limit, offset))