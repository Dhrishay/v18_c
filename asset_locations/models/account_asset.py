from odoo import _,fields, models, api
from odoo.exceptions import ValidationError


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    location_id = fields.Many2one('stock.location', 'Location', tracking=True)
    serial_no = fields.Char("Serial No")
    product_id = fields.Many2one('product.product', string='Product')
    product_tmpl_id = fields.Many2one('product.template', string='Product Template')
    user_id = fields.Many2one('res.users', 'Approver')
    picking_ids = fields.One2many("stock.picking", "asset_id")
    picking_id_count = fields.Integer(string="Total Pickings", compute="_compute_picking_ids")
    delivery_id_count = fields.Integer(string="Total Delivery", compute="_compute_delivery_ids")
    location_dest_id = fields.Many2one('stock.location', 'Destination Location')
    note = fields.Text('Notes', tracking=True)
    asset_code = fields.Char('Asset Code')
    sale_order_ids = fields.One2many("sale.order", "asset_id")
    sale_id_count = fields.Integer(string="Sales", compute="_compute_sale_order_ids")
    account_move_ids = fields.One2many("account.move", "asset_id")
    account_move_count = fields.Integer(string="Invoices", compute="_compute_account_move_ids")

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountAsset, self).create(vals_list)
        if self.env.context.get('is_create_chart_account', False) and self.env.context.get('active_id', False):
            account = self.env['account.account'].search([
                ('id', '=', int(self.env.context.get('active_id')))
            ])
            account.asset_model_ids = [(6, 0, res.ids)]
            account.is_create_model = True
        return res

    @api.depends('picking_ids')
    def _compute_picking_ids(self):
        for rec in self:
            picking_ids = rec._get_picking_ids()
            rec.picking_id_count = len(picking_ids or [])

    def _get_picking_ids(self):
        picking_list = []
        stock_picking = self.env["stock.picking"].search([
            ('is_asset_tranfer', '=', True)
        ])
        for picking in stock_picking:
            if self.id in picking.asset_id.ids:
                picking_list.append(picking.id)
        return picking_list

    @api.depends('picking_ids')
    def _compute_delivery_ids(self):
        for rec in self:
            picking_ids = rec._get_delivery_ids()
            rec.delivery_id_count = len(picking_ids)

    def _get_delivery_ids(self):
        picking_list = []
        stock_picking = self.env["stock.picking"].search([
            ('is_asset_tranfer', '=', False)
        ])
        for picking in stock_picking:
            if self.id in picking.asset_id.ids:
                picking_list.append(picking.id)
        return picking_list

    @api.depends('sale_order_ids')
    def _compute_sale_order_ids(self):
        for rec in self:
            sale_order_ids = rec._get_sale_order_ids()
            rec.sale_id_count = len(sale_order_ids or [])


    def _get_sale_order_ids(self):
        sale_orders = self.env["sale.order"].search(
            [('asset_id', '=', self.id)]
        )
        return sale_orders.ids

    @api.depends('account_move_ids')
    def _compute_account_move_ids(self):
        for rec in self:
            account_move_ids = rec._get_account_move_ids()
            rec.account_move_count = len(account_move_ids)

    def _get_account_move_ids(self):
        account_move_list = []
        account_moves = self.env["account.move"].search([
            ('is_created_from_asset', '=', True)
        ])
        for move in account_moves:
            if self.id in move.asset_id.ids:
                account_move_list.append(move.id)
        return account_move_list

    def _get_serial_numbers_from_bill(self):
        """Fetch serial numbers from the given vendor bill"""
        self._cr.execute("""DELETE FROM serial_numbers where company_id=%s""" % self.company_id.id) 
        bill_id = False
        if len(self.original_move_line_ids) == 1:
            bill_id =self.original_move_line_ids.move_id.id
        bill = self.env['account.move'].browse(bill_id)
        serial_numbers = []

        for line in bill.invoice_line_ids:
            stock_moves = self.env['stock.move'].search([
                ('purchase_line_id', '=', line.purchase_line_id.id),
                ('state', '=', 'done')  # Only completed stock moves
            ])
            if not stock_moves:
                raise ValidationError(_('You cannot validate this order receipt!'))

            for move in stock_moves:
                move_lines = self.env['stock.move.line'].search([
                    ('move_id', '=', move.id),
                    ('lot_id', '!=', False)
                ])
                if not move_lines:
                    raise ValidationError(_('You can not generate a serial number or validate the picking for this order.'))

                for move_line in move_lines:
                    if move_line.lot_id.name not in self.linked_assets_ids.mapped('serial_no'):
                        serial_numbers.append(move_line.lot_id.name)
                        self.env['serial.numbers'].create({
                            'name': move_line.lot_id.name
                        })
        return serial_numbers


    def action_confirm(self):
        company = self.env.company if not self.env.company.parent_id else self.env.company.parent_id
        if self.model_id and self.model_id.account_asset_id and self.model_id.account_asset_id.class_code:
            sequence = 'account.account.%s.%s' % (self.model_id.account_asset_id.id, company.id)
            self.asset_code = self.env['ir.sequence'].next_by_code(sequence)
        serial_numbres = self._get_serial_numbers_from_bill()
        if len(serial_numbres) == 0:
            self._cr.execute("""DELETE FROM serial_numbers where company_id=%s""" % self.company_id.id)
            name = 'Asset' +' '+ self.name
            product_id = self.env['product.product'].search([('name', '=', name)], limit=1)
            lot_final = self.env['stock.lot'].search([('product_id', '=', product_id.id)], limit=1)
            if lot_final:
                self.env['serial.numbers'].create({
                    'name': lot_final.name
                })
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'asset.serial.number',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_asset_id': self.id,
                        'default_check_lot': True,
                        'default_lot_id': lot_final.id,
                        'default_product_id': product_id.id,
                    },
                }
            else:
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'asset.serial.number',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_asset_id': self.id,
                    },
                }
        else:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'serial.number.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_asset_id': self.id,
                },
            } 

    def change_product_location(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'asset.change.location.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_asset_id': self.id,
            },
        }

    def create_internal_tranfer(self):
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'internal'), ('company_id', '=', self.company_id.id)], limit=1)
        stock_picking_vals = {
            'origin': self.name,
            'picking_type_id': picking_type.id,
            'location_dest_id': self.location_id.id,
            'scheduled_date': fields.Datetime.now(),
            'asset_id': self.id,
            'is_asset_tranfer': True,
            'user_id': self.user_id.id,
            'note': self.note,
        }
        stock_picking = self.env['stock.picking'].sudo().create(stock_picking_vals)
        stock_picking.update({'company_id': self.company_id.id})
        stock_data = {
            'picking_id': stock_picking.id,
            'date': fields.Datetime.now(),
            'name': self.name,
            'reference': self.name,
            'location_id': stock_picking.location_id.id,
            'location_dest_id': self.location_id.id,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_id.id,
            'product_uom_qty': 1,
            'quantity': 1,
            'company_id': self.company_id.id,
        }
        stock_move_id = self.env['stock.move'].sudo().create(stock_data)
        stock_move_id.update({
            'company_id': self.company_id.id
        })
        lot = self.env['stock.lot'].search([
            ('name', '=', self.serial_no),
            ('product_id', '=', self.product_id.id)
        ], limit=1)
        lot.update({
            'location_id': self.location_id.id
        })
        if not lot:
            raise UserError(f"Serial number {self.serial_no} not found for product {self.product_id.display_name}")

        # Create stock move line for serial number
        stock_move_line_vals = {
            'move_id': stock_move_id.id,
            'picking_id': stock_picking.id,
            'location_id': self.location_id.id,  # Source location
            'location_dest_id': self.location_id.id,  # Destination location
            'product_id': self.product_id.id,
            'lot_id': lot.id,
            'qty_done': 1,
            'product_uom_id': self.product_id.uom_id.id,
            'company_id': self.company_id.id,
        }
        move_lines = self.env['stock.move.line'].sudo().create(stock_move_line_vals)
        move_lines.update({
            'company_id': self.company_id.id
        })
        stock_picking.sudo().action_confirm()
        stock_picking.sudo().button_validate()
        return True

    def action_view_picking(self):
        action = {
            "name": _("Internal Transfers"),
            "res_model": "stock.picking",
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "domain": [("id", "in", self._get_picking_ids())],
            "context": {'create': False},
        }
        return action

    def action_asset_modify(self):
        """ Returns an action opening the asset modification wizard.
        """
        self.ensure_one()
        new_wizard = self.with_context(default_product_id=self.product_id.id).env['asset.modify'].create({
            'asset_id': self.id,
            'modify_action': 'resume' if self.env.context.get('resume_after_pause') else 'dispose',
        })
        return {
            'name': _('Modify Asset'),
            'view_mode': 'form',
            'res_model': 'asset.modify',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': new_wizard.id,
            'context': self.env.context,
        }

    def action_view_sale_order(self):
        action = {
            "name": _("Sales"),
            "res_model": "sale.order",
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "domain": [("id", "in", self._get_sale_order_ids())],
            "context": {'create': False},
        }
        return action

    def action_view_account_move(self):
        action = {
            "name": _("Invoices"),
            "res_model": "account.move",
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "domain": [("id", "in", self._get_account_move_ids())],
            "context": {'create': False},
        }
        return action

    def action_view_delivery(self):
        action = {
            "name": _("Delivery"),
            "res_model": "stock.picking",
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "domain": [("id", "in", self._get_delivery_ids())],
            "context": {'create': False},
        }
        return action