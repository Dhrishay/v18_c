from odoo import fields
from odoo import http
from odoo.http import request, route
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.tools.json import scriptsafe as json_scriptsafe
from odoo.addons.payment import utils as payment_utils
from datetime import datetime, timedelta
import pytz
from odoo.exceptions import UserError

class WebsiteSaleCustom(WebsiteSale):

     def float_to_float_time(self, float_time):
          """Convert float time to string time."""
          hours = int(float_time)
          minutes = int((float_time - hours) * 60)
          return f"{hours:02d}:{minutes:02d}"

     def _check_order_time_restriction(self):
          print("\n\n\n_check_order_time_restriction-------------------------------------")
          """Check if ordering is allowed based on time restrictions."""
          day_map = {
               'monday': 'mon', 'tuesday': 'tue', 'wednesday': 'wed',
               'thursday': 'thu', 'friday': 'fri', 'saturday': 'sat', 'sunday': 'sun',
          }

          company = request.env.company
          start_time_float = company.order_start_time
          end_time_float = company.order_end_time
          rule_id = company.rule_id

          if start_time_float and end_time_float:
               tz = pytz.timezone('Asia/Kolkata')
               now = datetime.now(tz)
               now_local = now.time()
               today_day_code = day_map[now.strftime('%A').lower()]

               if rule_id:
                    rule_record = request.env['order.day.rule'].search([('id', '=', rule_id.id)])
                    for line in rule_record.line_ids:
                         if line.day_of_week == today_day_code:
                              line_start_time_str = self.float_to_float_time(line.start_time)
                              line_end_time_str = self.float_to_float_time(line.end_time)

                              start_time = datetime.strptime(line_start_time_str, "%H:%M").time()
                              end_time = datetime.strptime(line_end_time_str, "%H:%M").time()

                              if start_time <= now_local <= end_time:
                                   pass
                                   # raise UserError(
                                   #      f"Ordering is not allowed between {start_time.strftime('%I:%M %p')} and {end_time.strftime('%I:%M %p')}."
                                   # )
               else:
                    start_time_str = self.float_to_float_time(start_time_float)
                    end_time_str = self.float_to_float_time(end_time_float)

                    start_time = datetime.strptime(start_time_str, "%H:%M").time()
                    end_time = datetime.strptime(end_time_str, "%H:%M").time()

                    if start_time <= now_local <= end_time:
                         return {
                              'restricted': True,
                              'message': f"Ordering is not allowed between {start.strftime('%I:%M %p')} and {end.strftime('%I:%M %p')}."
                         }
          return {'restricted': False}

     @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True)
     def cart_update_json(
             self, product_id, line_id=None, add_qty=None, set_qty=None, display=True,
             product_custom_attribute_values=None, no_variant_attribute_value_ids=None, **kwargs
     ):
          print("\n\n\ncart_update_json---------------custom----------------------")
          """Override to add time restriction check."""
          # Check time restrictions
          restriction_result = self._check_order_time_restriction()

          if restriction_result.get('restricted'):
               order = request.website.sale_get_order()
               return {
                    'notification_info': {
                         'has_error': True,
                         'modal': True,
                         'message': restriction_result['message'],
                         'type': 'warning',
                    },
                    'cart_quantity': order.cart_quantity if order else 0,
               }

          # Proceed with original logic
          return super(WebsiteSaleCustom, self).cart_update_json(
               product_id=product_id,
               line_id=line_id,
               add_qty=add_qty,
               set_qty=set_qty,
               display=display,
               product_custom_attribute_values=product_custom_attribute_values,
               no_variant_attribute_value_ids=no_variant_attribute_value_ids,
               **kwargs
          )

     @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
     def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
          print("\n\n\ncart_update----------------custom---------------------------")
          """Override to add time restriction check.
          This method is called when updating cart from the cart page."""
          # Check time restrictions
          self._check_order_time_restriction()

          # Continue with the original method
          return super(WebsiteSaleCustom, self).cart_update(
               product_id=product_id,
               add_qty=add_qty,
               set_qty=set_qty,
               **kw
          )

     # def float_to_float_time(self, float_value):
     #      hours = int(float_value)
     #      minutes = int((float_value - hours) * 60)
     #      return f"{hours:02d}:{minutes:02d}"
     #
     # def _check_order_time_restrictions(self, product_id):
     #      print("\n\n\n_check_order_time_restrictions--------------------------------")
     #      day_map = {
     #           'monday': 'mon', 'tuesday': 'tue', 'wednesday': 'wed',
     #           'thursday': 'thu', 'friday': 'fri', 'saturday': 'sat', 'sunday': 'sun',
     #      }
     #
     #      company = request.env.company
     #      start_time_float = company.order_start_time
     #      end_time_float = company.order_end_time
     #      rule_id = company.rule_id
     #
     #      tz = pytz.timezone('Asia/Kolkata')
     #      now = datetime.now(tz)
     #      now_local = now.time()
     #      today_day_code = day_map[now.strftime('%A').lower()]
     #
     #      if start_time_float and end_time_float:
     #           if rule_id:
     #                rule_record = request.env['order.day.rule'].browse(rule_id.id)
     #                product = request.env['product.product'].browse(product_id)
     #                product_category = product.categ_id
     #
     #                for line in rule_record.line_ids:
     #                     if line.day_of_week == today_day_code:
     #                          line_start = datetime.strptime(self.float_to_float_time(line.start_time), "%H:%M").time()
     #                          line_end = datetime.strptime(self.float_to_float_time(line.end_time), "%H:%M").time()
     #
     #                          if product_category in line.category_ids and line_start <= now_local <= line_end:
     #                               raise UserError(
     #                                    f"Ordering is not allowed for category '{product_category.name}' "
     #                                    f"between {line_start.strftime('%I:%M %p')} and {line_end.strftime('%I:%M %p')} on {today_day_code.capitalize()}."
     #                               )
     #      else:
     #           start_time = datetime.strptime(self.float_to_float_time(start_time_float), "%H:%M").time()
     #           end_time = datetime.strptime(self.float_to_float_time(end_time_float), "%H:%M").time()
     #
     #           if start_time <= now_local <= end_time:
     #                raise UserError(
     #                     f"Ordering is not allowed between {start_time.strftime('%I:%M %p')} and {end_time.strftime('%I:%M %p')}."
     #                )
     #
     # @route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True)
     # def cart_update_json(
     #         self, product_id, line_id=None, add_qty=None, set_qty=None, display=True,
     #         product_custom_attribute_values=None, no_variant_attribute_value_ids=None, **kwargs
     # ):
     #      print("\n\n\ncart_update_json-----------custome--------------------------------------")
     #      print("product_id------------------------------",product_id)
     #
     #      """
     #      This route is called :
     #          - When changing quantity from the cart.
     #          - When adding a product from the wishlist.
     #          - When adding a product to cart on the same page (without redirection).
     #      """
     #      day_map = {
     #           'monday': 'mon', 'tuesday': 'tue', 'wednesday': 'wed',
     #           'thursday': 'thu', 'friday': 'fri', 'saturday': 'sat', 'sunday': 'sun',
     #      }
     #
     #      company = request.env.company
     #      print("company----------------------------",company)
     #      start_time_float = company.order_start_time
     #      end_time_float = company.order_end_time
     #      rule_id = company.rule_id
     #
     #      if start_time_float and end_time_float:
     #           tz = pytz.timezone('Asia/Kolkata')
     #           print("tz-------------------------",tz)
     #           now = datetime.now(tz)
     #           now_local = now.time()
     #           # print("now_local-------------------------",now_local)
     #           today_day_code = day_map[now.strftime('%A').lower()]
     #           # print("today_day---------------------",today_day_code)
     #           if rule_id:
     #                print("rule_id---------------------------")
     #                rule_record = request.env['order.day.rule'].search([('id', '=', rule_id.id)])
     #                print("rule_record------------------------",rule_record)
     #                product = request.env['product.product'].browse(product_id)
     #                print("product---------------------------",product)
     #                product_category = product.categ_id
     #                print("product_category-----------------------",product_category)
     #                for line in rule_record.line_ids:
     #                     print("line-------------------", line.day_of_week)
     #                     if line.day_of_week == today_day_code:
     #                          print("if lower day---------------------------------")
     #
     #                          line_start_time_str = self.float_to_float_time(line.start_time)
     #                          print("line_start_time_str----22-------------", line_start_time_str)
     #                          line_end_time_str = self.float_to_float_time(line.end_time)
     #                          print("line_end_time_str----22-------------", line_end_time_str)
     #
     #                          start_time = datetime.strptime(line_start_time_str, "%H:%M").time()
     #                          print("start_time--------22---------", start_time)
     #                          end_time = datetime.strptime(line_end_time_str, "%H:%M").time()
     #                          print("start_time------22-----------", end_time)
     #
     #                          if start_time <= now_local <= end_time:
     #                               print("iff---------************-----------")
     #                               raise UserError(
     #                                    f"Ordering is not allowed between {start_time.strftime('%I:%M %p')} and {end_time.strftime('%I:%M %p')}."
     #                               )
     #
     #           else:
     #                start_time_str = self.float_to_float_time(start_time_float)
     #                print("start_time----11-------------", start_time_str)
     #                end_time_str = self.float_to_float_time(end_time_float)
     #                print("end_time:-------222------------", end_time_str)
     #
     #                start_time = datetime.strptime(start_time_str, "%H:%M").time()
     #                print("start_time-----------------", start_time)
     #                end_time = datetime.strptime(end_time_str, "%H:%M").time()
     #                print("start_time-----------------", end_time)
     #                print("else-----------------")
     #                if start_time <= now_local <= end_time:
     #                     print("if1111")
     #                     raise UserError(
     #                          f"Ordering is not allowed between {start_time.strftime('%I:%M %p')} and {end_time.strftime('%I:%M %p')}."
     #                     )
     #
     #      order = request.website.sale_get_order(force_create=True)
     #      if order.state != 'draft':
     #           request.website.sale_reset()
     #           if kwargs.get('force_create'):
     #                order = request.website.sale_get_order(force_create=True)
     #           else:
     #                return {}
     #
     #      if product_custom_attribute_values:
     #           product_custom_attribute_values = json_scriptsafe.loads(product_custom_attribute_values)
     #
     #      # old API, will be dropped soon with product configurator refactorings
     #      no_variant_attribute_values = kwargs.pop('no_variant_attribute_values', None)
     #      if no_variant_attribute_values and no_variant_attribute_value_ids is None:
     #           no_variants_attribute_values_data = json_scriptsafe.loads(no_variant_attribute_values)
     #           no_variant_attribute_value_ids = [
     #                int(ptav_data['value']) for ptav_data in no_variants_attribute_values_data
     #           ]
     #
     #      values = order._cart_update(
     #           product_id=product_id,
     #           line_id=line_id,
     #           add_qty=add_qty,
     #           set_qty=set_qty,
     #           product_custom_attribute_values=product_custom_attribute_values,
     #           no_variant_attribute_value_ids=no_variant_attribute_value_ids,
     #           **kwargs
     #      )
     #
     #      # If the line is a combo product line, and it already has combo items, we need to update
     #      # the combo item quantities as well.
     #      line = request.env['sale.order.line'].browse(values['line_id'])
     #      if line.product_type == 'combo' and line.linked_line_ids:
     #           quantity = values['quantity']
     #           combo_quantity = quantity
     #           # A combo product and its items should have the same quantity (by design). So, if the
     #           # requested quantity isn't available for one or more combo items, we should lower the
     #           # quantity of the combo product and its items to the maximum available quantity of the
     #           # combo item with the least available quantity.
     #           for linked_line in line.linked_line_ids:
     #                if quantity != linked_line.product_uom_qty:
     #                     combo_item_quantity, warning = order._verify_updated_quantity(
     #                          linked_line, linked_line.product_id.id, quantity, **kwargs
     #                     )
     #                     combo_quantity = min(combo_quantity, combo_item_quantity)
     #           for linked_line in line.linked_line_ids:
     #                order._cart_update(
     #                     product_id=linked_line.product_id.id,
     #                     line_id=linked_line.id,
     #                     set_qty=combo_quantity,
     #                     **kwargs,
     #                )
     #           if combo_quantity < quantity:
     #                order._cart_update(
     #                     product_id=product_id,
     #                     line_id=line_id,
     #                     set_qty=combo_quantity,
     #                     **kwargs,
     #                )
     #
     #      values['notification_info'] = self._get_cart_notification_information(order, [values['line_id']])
     #      values['notification_info']['warning'] = values.pop('warning', '')
     #      request.session['website_sale_cart_quantity'] = order.cart_quantity
     #
     #      if not order.cart_quantity:
     #           request.website.sale_reset()
     #           return values
     #
     #      values['cart_quantity'] = order.cart_quantity
     #      values['minor_amount'] = payment_utils.to_minor_currency_units(
     #           order.amount_total, order.currency_id
     #      )
     #      values['amount'] = order.amount_total
     #
     #      if not display:
     #           return values
     #
     #      values['cart_ready'] = order._is_cart_ready()
     #      values['website_sale.cart_lines'] = request.env['ir.ui.view']._render_template(
     #           "website_sale.cart_lines", {
     #                'website_sale_order': order,
     #                'date': fields.Date.today(),
     #                'suggested_products': order._cart_accessories()
     #           }
     #      )
     #      values['website_sale.total'] = request.env['ir.ui.view']._render_template(
     #           "website_sale.total", {
     #                'website_sale_order': order,
     #           }
     #      )
     #      return values
     #
