# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class PosCategory(models.Model):
    _inherit = "pos.category"

    # @api.model
    # def _load_pos_data_domain(self, data):
    #     print("\n\n\n_load_pos_data_domain---------******---------------------")
    #     config_id = self.env['pos.config'].browse(data['pos.config']['data'][0]['id'])
    #     # print("config_id---------------------------------",config_id)
    #     domain = [('id', 'in', config_id._get_available_categories().ids)] if config_id.limit_categories and config_id.iface_available_categ_ids and config_id.product_load_background and config_id.limited_products_loading else []
    #     return domain


    # @api.model
    # def _load_pos_data_domain(self, data):
    #     config_id = self.env['pos.config'].browse(data['pos.config']['data'][0]['id'])
    #     # Load categories according to loaded products
    #     product_catg_ids = []
    #     for product in data['product.product']['data']:
    #         product_catg_ids += product['pos_categ_ids']
    #     if config_id.limit_categories and config_id.iface_available_categ_ids and config_id.product_load_background and config_id.limited_products_loading:
    #         product_catg_ids = config_id._get_available_categories().ids
    #     elif config_id.limit_categories and config_id.iface_available_categ_ids and not config_id.product_load_background and not config_id.limited_products_loading:
    #         category_ids = config_id._get_available_categories().ids
    #         product_catg_ids = list(set(product_catg_ids) & set(category_ids))
    #     return [('id', 'in', product_catg_ids)]