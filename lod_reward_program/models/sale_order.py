# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.fields import Command
import random
from odoo.tools import float_round
from collections import defaultdict
import itertools

def _generate_random_reward_code():
    return str(random.getrandbits(32))


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    
    def _get_claimable_rewards(self, forced_coupons=None):
        res = super()._get_claimable_rewards(forced_coupons=forced_coupons)
        print("d;;;;;;;;;;;;;;d;d;d;d", res)
        return res


    def _get_reward_values_product(self, reward, coupon, product=None, **kwargs):
            """
            Returns an array of dict containing the values required for the reward lines.
            Override this method for gift multiple product.
            """
            self.ensure_one()
            assert reward.reward_type == 'product'

            reward_products = reward.reward_product_ids

            taxes = self.fiscal_position_id.map_tax(reward_products.taxes_id._filter_taxes_by_company(self.company_id))
            points = self._get_real_points_for_coupon(coupon)
            claimable_count = float_round(points / reward.required_points, precision_rounding=1, rounding_method='DOWN') if not reward.clear_wallet else 1
            cost = points if reward.clear_wallet else claimable_count * reward.required_points

            vals_list = []

            for product in reward_products:
                vals_list.append({
                'name': _("Free Product - %(product)s", product=product.with_context(display_default_code=False).display_name),
                'product_id': product.id,
                'discount': 100,
                'product_uom_qty': reward.reward_product_qty * claimable_count,
                'reward_id': reward.id,
                'coupon_id': coupon.id,
                'points_cost': cost,
                'reward_identifier_code': _generate_random_reward_code(),
                'product_uom': product.uom_id.id,
                'sequence': max(self.order_line.filtered(lambda x: not x.is_reward_line).mapped('sequence'), default=10) + 1,
                'tax_id': [(Command.CLEAR, 0, 0)] + [(Command.LINK, tax.id, False) for tax in taxes]
            })

            return vals_list
    
    #Override function for set specific discount on selected product
    def _discountable_specific(self, reward):
        """
        Special function to compute the discountable for 'specific' types of discount.
        The goal of this function is to make sure that applying a 5$ discount on an order with a
         5$ product and a 5% discount does not make the order go below 0.

        Returns the discountable and discountable_per_tax for a discount that only applies to specific products.
        """
        self.ensure_one()
        assert reward.discount_applicability == 'specific'

        lines_to_discount = self._get_specific_discountable_lines(reward).filtered(
            lambda line: bool(line.product_uom_qty and line.price_total)
        )
        discount_lines = defaultdict(lambda: self.env['sale.order.line'])
        order_lines = self.order_line - self._get_no_effect_on_threshold_lines()
        remaining_amount_per_line = defaultdict(int)
        for line in order_lines:
            if not line.product_uom_qty or not line.price_total:
                continue
            remaining_amount_per_line[line] = line.price_total
            if line.reward_id.reward_type == 'discount':
                discount_lines[line.reward_identifier_code] |= line

        order_lines -= self.order_line.filtered("reward_id")
        cheapest_line = False
        for lines in discount_lines.values():
            line_reward = lines.reward_id
            discounted_lines = order_lines
            if line_reward.discount_applicability == 'cheapest':
                cheapest_line = cheapest_line or self._cheapest_line()
                discounted_lines = cheapest_line
            elif line_reward.discount_applicability == 'specific':
                discounted_lines = self._get_specific_discountable_lines(line_reward)
            if not discounted_lines:
                continue
            common_lines = discounted_lines & lines_to_discount
            if line_reward.discount_mode == 'percent':
                for line in discounted_lines:
                    if line_reward.discount_applicability == 'cheapest':
                        remaining_amount_per_line[line] *= (1 - line_reward.discount / 100 / line.product_uom_qty)
                    else:
                        remaining_amount_per_line[line] *= (1 - line_reward.discount / 100)
            else:
                non_common_lines = discounted_lines - lines_to_discount
                # Fixed prices are per tax
                discounted_amounts = defaultdict(int, {
                    line.tax_id.filtered(lambda t: t.amount_type != 'fixed'): abs(line.price_total)
                    for line in lines
                })
                for line in itertools.chain(non_common_lines, common_lines):
                    # For gift card and eWallet programs we have no tax but we can consume the amount completely
                    if lines.reward_id.program_id.is_payment_program:
                        discounted_amount = discounted_amounts[lines.tax_id.filtered(lambda t: t.amount_type != 'fixed')]
                    else:
                        discounted_amount = discounted_amounts[line.tax_id.filtered(lambda t: t.amount_type != 'fixed')]
                    if discounted_amount == 0:
                        continue
                    remaining = remaining_amount_per_line[line]
                    consumed = min(remaining, discounted_amount)
                    if lines.reward_id.program_id.is_payment_program:
                        discounted_amounts[lines.tax_id.filtered(lambda t: t.amount_type != 'fixed')] -= consumed
                    else:
                        discounted_amounts[line.tax_id.filtered(lambda t: t.amount_type != 'fixed')] -= consumed
                    remaining_amount_per_line[line] -= consumed

        discountable = 0
        discountable_per_tax = defaultdict(int)
        for line in lines_to_discount:
            discountable +=  remaining_amount_per_line[line]
            line_discountable = line.price_unit * line.product_uom_qty * (1 - (line.discount or 0.0) / 100.0)
            # line_discountable is the same as in a 'order' discount
            #  but first multiplied by a factor for the taxes to apply
            #  and then multiplied by another factor coming from the discountable

            if reward.program_type == 'promotion':
                line_tax = line.tax_id
                line.sudo().update({'tax_id': False})
                taxes = line.tax_id.filtered(lambda t: t.amount_type != 'fixed')
                discountable_per_tax[taxes] += line_discountable *\
                    (remaining_amount_per_line[line] / line.price_total)
                line.sudo().update({'tax_id': line_tax})
            else:
                taxes = line.tax_id.filtered(lambda t: t.amount_type != 'fixed')
                discountable_per_tax[taxes] += line_discountable *\
                (remaining_amount_per_line[line] / line.price_total)
        return discountable, discountable_per_tax