# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Laoodoo
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    is_multi_currency = fields.Boolean(
        related='config_id.multi_currency_payment', readonly=False
    )


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ['inverse_rate']
        return params

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, load=False):
        if 'check_from_pos' in self.env.context:
            domain = []
            res = super(ResCurrency, self).search_read(
                domain=domain, fields=fields, offset=offset, limit=limit,
                order=order, load=load
            )
            for curr in res:
                currency_obj = self.browse([curr.get('id')]).rate_ids
                for currency in currency_obj: 
                    formatted_inverse =   currency.rate_sale  
                    formatted_rate =  currency.inver_rate_sale 
  
                    curr.update({
                        'rate': formatted_inverse,
                        'inverse_rate': formatted_rate  ,
                    }) 
            return res
        return super(ResCurrency, self).search_read(
            domain=domain, fields=fields, offset=offset, limit=limit,
            order=order, load=load
        )
