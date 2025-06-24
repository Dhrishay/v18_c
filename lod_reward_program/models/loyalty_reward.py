# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import  api, models, fields


class LoyaltyReward(models.Model):
    _inherit = 'loyalty.reward'

    rule_id = fields.Many2one('loyalty.rule', string="Rule")


    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ['rule_id', 'discount_product_ids']
        return params
    

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'
    reward_ids = fields.Many2many('loyalty.reward', string="Rewards")
    
    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ['reward_ids']
        return params
