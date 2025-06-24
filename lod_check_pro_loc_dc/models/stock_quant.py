# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from datetime import datetime, timedelta
import datetime
from dateutil.relativedelta import relativedelta
from ast import literal_eval


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    barcode = fields.Char(related='product_id.barcode', string='Barcode', store=True)

    @api.model
    def action_view_inventory_cyc(self):
        """ Similar to _get_quants_action except specific for inventory adjustments (i.e. inventory counts). """
        self = self._set_view_context()
        self._quant_tasks()

        ctx = dict(self.env.context or {})
        ctx['no_at_date'] = True
        # ctx['inventory_quantity_set'] = True
        if self.user_has_groups('stock.group_stock_user') and not self.user_has_groups('stock.group_stock_manager'):
            ctx['search_default_my_count'] = True
        action = {
            'name': _('Cycle Counts'),
            'view_mode': 'list',
            'view_id': self.env.ref('stock.view_stock_quant_tree_inventory_editable').id,
            'res_model': 'stock.quant',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': [('location_id.usage', 'in', ['internal', 'transit']), ('inventory_date', '&lt;=', self.env.context_today().strftime('%Y-%m-%d'))],
            'help': """
                <p class="o_view_nocontent_smiling_face">
                    {}
                </p><p>
                    {} <span class="fa fa-long-arrow-right"/> {}</p>
                """.format(_('Your stock is currently empty'),
                           _('Press the CREATE button to define quantity for each product in your stock or import them from a spreadsheet throughout Favorites'),
                           _('Import')),
        }
        return action