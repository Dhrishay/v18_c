from odoo import fields
from odoo import http
from odoo.http import request, route
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.tools.json import scriptsafe as json_scriptsafe
from odoo.addons.payment import utils as payment_utils
from datetime import datetime, timedelta
import pytz
from odoo.exceptions import UserError
from odoo.addons.website_sale.controllers.product_configurator import WebsiteSaleProductConfiguratorController

class WebsiteSaleCustom(WebsiteSale):

     def float_to_float_time(self, float_time):
          """Convert float time to string time."""
          hours = int(float_time)
          minutes = int((float_time - hours) * 60)
          return f"{hours:02d}:{minutes:02d}"

     def _check_order_time_restriction(self, product_id=None):
          day_map = {
               'monday': 'mon', 'tuesday': 'tue', 'wednesday': 'wed',
               'thursday': 'thu', 'friday': 'fri', 'saturday': 'sat', 'sunday': 'sun',
          }

          company = request.env.company
          start_time_float = company.order_start_time
          end_time_float = company.order_end_time
          rule_id = company.rule_id

          user = request.env.user
          user_tz = user.tz or 'UTC'
          tz = pytz.timezone(user_tz)
          now = datetime.now(tz)
          now_local = now.time()

          if not product_id:
               return {'warning': 'Product information is missing.'}

          product = request.env['product.product'].browse(int(product_id))
          product_category = product.categ_id

          if start_time_float and end_time_float and rule_id:
               today_day_code = day_map[now.strftime('%A').lower()]
               rule_record = request.env['order.day.rule'].browse(rule_id.id)
               today_lines = rule_record.line_ids.filtered(lambda l: l.day_of_week == today_day_code)
               if not today_lines:
                    return False

               restricted_categories = today_lines.mapped('category_ids')

               if product_category not in restricted_categories:
                    return False

               for line in today_lines:
                    if product_category in line.category_ids:
                         if line.start_time and line.end_time:
                              start_time = datetime.strptime(self.float_to_float_time(line.start_time), "%H:%M").time()
                              end_time = datetime.strptime(self.float_to_float_time(line.end_time), "%H:%M").time()
                         else:
                              start_time = datetime.strptime(self.float_to_float_time(start_time_float), "%H:%M").time()
                              end_time = datetime.strptime(self.float_to_float_time(end_time_float), "%H:%M").time()

                         if start_time <= now_local <= end_time:
                              return False
                         else:
                              return {
                                   'warning': f'You cannot add this product to cart now. Allowed categories for today ({now.strftime("%A")}) are time restricted.'
                              }

          if start_time_float and end_time_float:
               start_time_str = self.float_to_float_time(start_time_float)
               end_time_str = self.float_to_float_time(end_time_float)

               start_time = datetime.strptime(start_time_str, "%H:%M").time()
               end_time = datetime.strptime(end_time_str, "%H:%M").time()

               if not start_time <= now_local <= end_time:
                    return {
                         'warning': f'Adding to cart is currently not allowed. You can place orders between {start_time.strftime("%I:%M %p")} and {end_time.strftime("%I:%M %p")}.'
                    }
          return False

     @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True)
     def cart_update_json(
             self, product_id, line_id=None, add_qty=None, set_qty=None, display=True,
             product_custom_attribute_values=None, no_variant_attribute_value_ids=None, **kwargs
     ):
          """Override to add time restriction check."""
          # Check time restrictions
          time_restriction = self._check_order_time_restriction(product_id=product_id)
          if time_restriction:
               return time_restriction

          return super().cart_update_json(
               product_id=product_id,
               line_id=line_id,
               add_qty=add_qty,
               set_qty=set_qty,
               display=display,
               product_custom_attribute_values=product_custom_attribute_values,
               no_variant_attribute_value_ids=no_variant_attribute_value_ids,
               **kwargs,
          )

class WebsiteSaleProductConfiguratorCustom(WebsiteSaleProductConfiguratorController):

     @route(
          route='/website_sale/product_configurator/update_cart',
          type='json',
          auth='public',
          methods=['POST'],
          website=True,
     )
     def website_sale_product_configurator_update_cart(
             self, main_product, optional_products, **kwargs
     ):
          """ Add the provided main and optional products to the cart.

          Main and optional products have the following shape:
          ```
          {
              'product_id': int,
              'product_template_id': int,
              'parent_product_template_id': int,
              'quantity': float,
              'product_custom_attribute_values': list(dict),
              'no_variant_attribute_value_ids': list(int),
          }
          ```

          Note: if product A is a parent of product B, then product A must come before product B in
          the optional_products list. Otherwise, the corresponding order lines won't be linked.

          :param dict main_product: The main product to add.
          :param list(dict) optional_products: The optional products to add.
          :param dict kwargs: Locally unused data passed to `_cart_update`.
          :rtype: dict
          :return: A dict containing information about the cart update.
          """
          order_sudo = request.website.sale_get_order(force_create=True)
          if order_sudo.state != 'draft':
               request.session['sale_order_id'] = None
               order_sudo = request.website.sale_get_order(force_create=True)

          product_id = main_product.get("product_id")
          time_restriction = self._check_order_time_restriction(product_id=product_id)
          if time_restriction:
               return False

          # The main product could theoretically have a parent, but we ignore it to avoid
          # circularities in the linked line ids.
          values = order_sudo._cart_update(
               product_id=main_product['product_id'],
               add_qty=main_product['quantity'],
               product_custom_attribute_values=main_product['product_custom_attribute_values'],
               no_variant_attribute_value_ids=[
                    int(value_id) for value_id in main_product['no_variant_attribute_value_ids']
               ],
               **kwargs,
          )
          line_ids = {main_product['product_template_id']: values['line_id']}

          if optional_products and values['line_id']:
               for option in optional_products:
                    option_values = order_sudo._cart_update(
                         product_id=option['product_id'],
                         add_qty=option['quantity'],
                         product_custom_attribute_values=option['product_custom_attribute_values'],
                         no_variant_attribute_value_ids=[
                              int(value_id) for value_id in option['no_variant_attribute_value_ids']
                         ],
                         # Using `line_ids[...]` instead of `line_ids.get(...)` ensures that this throws
                         # if an optional product contains bad data.
                         linked_line_id=line_ids[option['parent_product_template_id']],
                         **kwargs,
                    )
                    line_ids[option['product_template_id']] = option_values['line_id']

          values['notification_info'] = self._get_cart_notification_information(
               order_sudo, line_ids.values()
          )
          values['cart_quantity'] = order_sudo.cart_quantity
          request.session['website_sale_cart_quantity'] = order_sudo.cart_quantity

          return values
