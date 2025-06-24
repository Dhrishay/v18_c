# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#   Copyright (C) 2016-today Geminate Consultancy Services (<http://geminatecs.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.model
    def _default_location_id(self):
        company_user = self.env.user.company_id
        warehouse = self.env['stock.warehouse'].sudo().search([
            ('company_id', '=', company_user.id)], limit=1
        )
        if warehouse and warehouse.lot_stock_id:
            return warehouse.lot_stock_id.id
        else:
            raise ValidationError(_(
                'You must define a warehouse for the company: %s.') % (company_user.name,)
            )

    adjst_location_id = fields.Many2one(
        'stock.location', 'Inventoried Location',
        domain="[('company_id', '=', company_id), ('usage', 'in', ['internal', 'transit'])]",
        default=_default_location_id
    )
    is_inventory_adjustment = fields.Boolean(string="Inventory Adjustment", default=False)
    is_multi_location = fields.Boolean(string="Is Multi Location", default=False)
    warehouse_name = fields.Char()


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    @api.model
    def _default_location_id(self):
        company_user = self.env.user.company_id
        warehouse = self.env['stock.warehouse'].sudo().search([
            ('company_id', '=', company_user.id)
        ], limit=1)
        if warehouse and warehouse.lot_stock_id:
            return warehouse.lot_stock_id.id
        else:
            raise ValidationError(_(
                'You must define a warehouse for the company: %s.') % (company_user.name,)
            )
    
    adjst_location_id = fields.Many2one(
        'stock.location', 'Inventoried Location',
        related='pos_config_id.adjst_location_id', index=True,readonly=False
    )
    is_inventory_adjustment = fields.Boolean(
        string="Inventory Adjustment",
        related='pos_config_id.is_inventory_adjustment',readonly=False
    )
    is_multi_location = fields.Boolean(
        string="Is Multi Location",
        related='pos_config_id.is_multi_location', readonly=False
    )
    warehouse_name = fields.Char(
        "Warehouse name",related='pos_config_id.warehouse_name',
        readonly=False
    )
