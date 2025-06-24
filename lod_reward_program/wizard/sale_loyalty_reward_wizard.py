# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class SaleLoyaltyRewardWizard(models.TransientModel):
    _inherit = 'sale.loyalty.reward.wizard'

    selected_reward_ids = fields.Many2many(
        'loyalty.reward', domain="[('id', 'in', reward_ids)]", string="loyalty rewards"
    )

    """
        Override this method for gift multiple product.
    """
    def action_apply(self):
        self.ensure_one()
        if not self.selected_reward_ids:
            raise ValidationError(_('No reward selected.'))
        claimable_rewards = self.order_id._get_claimable_rewards()

        for coupon, rewards in claimable_rewards.items():
            if any(reward in rewards for reward in self.selected_reward_ids):
                if not coupon:
                    raise ValidationError(
                        _('Coupon not found while trying to add the following reward: %s') %
                        self.selected_reward_ids[0].description
                    )
                # Apply rewards related to this coupon
                for s_reward in self.selected_reward_ids:
                    if s_reward in rewards:
                        self.order_id._apply_program_reward(s_reward, coupon, product=self.reward_product_ids)

        # Update programs and rewards after applying all valid rewards
        self.order_id._update_programs_and_rewards()
        return True