from odoo import models, fields
from datetime import datetime
import pytz
from odoo.exceptions import UserError


class SaleOrder(models.Model):
     _inherit = 'sale.order'

     def _cart_update(self, product_id, line_id=None, add_qty=0, set_qty=0, **kwargs):
          print("\n\n\n_cart_update----2222------------custom-----------------------")
          self.ensure_one()
          self._check_order_time_restriction()
          return super()._cart_update(product_id, line_id, add_qty, set_qty, **kwargs)

     def float_to_float_time(self, float_time):
          """Convert float time to string time."""
          hours = int(float_time)
          minutes = int((float_time - hours) * 60)
          return f"{hours:02d}:{minutes:02d}"

     def _check_order_time_restriction(self):
          print("\n\n\n_check_order_time_restriction----------222----custom-----------------------")
          """Check if ordering is allowed based on time restrictions."""
          day_map = {
               'monday': 'mon', 'tuesday': 'tue', 'wednesday': 'wed',
               'thursday': 'thu', 'friday': 'fri', 'saturday': 'sat', 'sunday': 'sun',
          }

          company = self.env.company
          start_time_float = company.order_start_time
          end_time_float = company.order_end_time
          rule_id = company.rule_id

          if start_time_float and end_time_float:
               tz = pytz.timezone('Asia/Kolkata')
               now = datetime.now(tz)
               now_local = now.time()
               today_day_code = day_map[now.strftime('%A').lower()]

               if rule_id:
                    rule_record = self.env['order.day.rule'].search([('id', '=', rule_id.id)])
                    for line in rule_record.line_ids:
                         if line.day_of_week == today_day_code:
                              line_start_time_str = self.float_to_float_time(line.start_time)
                              line_end_time_str = self.float_to_float_time(line.end_time)

                              start_time = datetime.strptime(line_start_time_str, "%H:%M").time()
                              end_time = datetime.strptime(line_end_time_str, "%H:%M").time()

                              if start_time <= now_local <= end_time:
                                   raise UserError(
                                        f"Ordering is not allowed between {start_time.strftime('%I:%M %p')} and {end_time.strftime('%I:%M %p')}."
                                   )
               else:
                    start_time_str = self.float_to_float_time(start_time_float)
                    end_time_str = self.float_to_float_time(end_time_float)

                    start_time = datetime.strptime(start_time_str, "%H:%M").time()
                    end_time = datetime.strptime(end_time_str, "%H:%M").time()

                    if start_time <= now_local <= end_time:
                         raise UserError(
                              f"Ordering is not allowed between {start_time.strftime('%I:%M %p')} and {end_time.strftime('%I:%M %p')}."
                         )