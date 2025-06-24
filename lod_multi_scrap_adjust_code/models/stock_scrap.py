from odoo import _, models, fields, api
from odoo.exceptions import UserError
from odoo.tools import float_compare


class MultiScrap(models.Model):
    _name = 'multi.scrap'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Multi Scrap'

    def _get_default_location_id(self):
        company_id = self.env.context.get(
            'default_company_id') or self.env.company.id
        return self.env['stock.location'].search([('company_id', 'in', [company_id, False])], limit=1).id

    name = fields.Char(string="Name", required=True, default="New")
    description = fields.Char(string="Description")
    origin = fields.Char('Source Document', index=True, help="Reference of the document")
    user_id = fields.Many2one(
        'res.users', string='Responsible', readonly=True, default=lambda self: self.env.user.id)
    order_line_ids = fields.One2many(
        'multi.scrap.line', 'scrap_adjust_id',
        string="Scrap Order Lines")
    stock_move_ids = fields.One2many(
        'stock.move', 'scrap_multi_id', string="Stock Move", readonly=True)
    stock_move_line_ids = fields.One2many(
        'stock.move.line', 'scrap_multi_id', string="Stock Move Lines", readonly=True)
    type_adjust = fields.Selection([('adjust', 'Adjustment'), ('scrap', 'Scrap')], required=True, default='adjust', string='Adjust Type')

    location_adjust = fields.Selection([
        ('dc', 'DC'),
        ('kkz', 'KKZ'),
        ('fc', 'KKM Store'),
    ], default='fc', string='Adjust Location')

    state = fields.Selection([
        ('wait_to_approve', 'Wait to Approve'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, default='wait_to_approve', tracking=True)
    date = fields.Datetime(string="Adjust Date", default=fields.Datetime.now(), required=True)
    reason_code_id = fields.Many2one('scrap.reason.code', string='Reason Code')
    received_loss = fields.Selection(related='reason_code_id.received_loss', string='Received/Loss')
    src_location_id = fields.Many2one('stock.location', string='Source Location', store=True)
    dest_location_id = fields.Many2one('stock.location', compute='_compute_location', string='Dest Location', store=True)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True, readonly=True)
    show_confirm = fields.Boolean(compute='_compute_show_confirm', help='Technical field used to compute whether the button "Mark as Todo" should be displayed.')

    def print_counted_report_xlsx(self):
        datas = {
            'model': 'stock.counted.wizard.report',
            'form': self.read()[0]
        }

        return self.env.ref("lod_multi_scrap_adjust_code.action_stock_summary_report_xlsx").report_action(
            self, data=datas
        )

    def action_done(self):
        operation_type = self.company_id.picking_type_id
        if not operation_type:
            raise UserError(_('No operation type for this transfer'))
        else:
            if self.type_adjust in ['adjust', 'scrap']:
                stock_picking_vals = {
                    'origin': self.name,
                    'picking_type_id': operation_type.id,
                    'location_id': self.src_location_id.id,
                    'location_dest_id': self.dest_location_id.id,
                    'scheduled_date': fields.Datetime.now(),
                }

                stock_picking = self.env['stock.picking']. \
                    sudo().create(stock_picking_vals)
                for line in self.order_line_ids:
                    stock_quant = self.env['stock.quant'].search(
                        [('product_id', '=', line.product_id.id),
                         ('on_hand', '=', True)])
                    location = stock_quant.mapped('location_id')

                    stock_data = {
                        'scrap_multi_id': self.id,
                        'picking_id': stock_picking.id,
                        'reason_code_id': self.reason_code_id.id,
                        'date': fields.Datetime.now(),
                        'name': self.reason_code_id.name,
                        'reference': self.reason_code_id.name,
                        'location_id': line.src_location_id.id,
                        'location_dest_id': line.dest_location_id.id,
                        'product_id': line.product_id.id,
                        'product_uom_qty': abs(line.diff_qty),
                        'quantity': abs(line.diff_qty),
                        'product_uom': line.uom_id.id,
                        'company_id': self.company_id.id,
                    }
                    stock_move_id = self.env['stock.move'].create(stock_data)
                    stock_move_id.move_line_ids.write({'scrap_multi_id': self.id})
                stock_picking.action_confirm()
                stock_picking.sudo().button_validate()

            elif self.type_adjust in 'unpackbox':
                for line in self.order_line_ids:
                    if line.uom_id.name == 'Unit':
                        move_unit = self.env['stock.move'].create({
                            'name': self.reason_code_id.name,
                            'location_id': line.src_location_id.id,
                            'location_dest_id': line.dest_location_id.id,
                            'product_id': line.product_id.id,
                            'product_uom': line.uom_id.id,
                            'product_uom_qty': abs(line.diff_qty),
                        })
                        move_unit.move_line_ids = False
                        move_unit._action_confirm()
                        move_unit._action_assign()
                        move_unit.move_line_ids.write({'qty_done': abs(line.diff_qty), 'scrap_multi_id': self.id,
                                                       'reason_code_id': self.reason_code_id.id})
                        move_unit._action_done()
                        # raise UserError(_('Product Name: %s %s is not Pack or Box') % (line.product_id.barcode,line.product_id.name))
                    else:
                        move_box = self.env['stock.move'].create({
                            'name': self.reason_code_id.name,
                            'location_id': line.src_location_id.id,
                            'location_dest_id': line.dest_location_id.id,
                            'product_id': line.product_id.id,
                            'product_uom': line.uom_id.id,
                            'product_uom_qty': abs(line.diff_qty),
                        })
                        move_box.move_line_ids = False
                        move_box._action_confirm()
                        move_box._action_assign()
                        move_box.move_line_ids.write({'qty_done': abs(line.diff_qty), 'scrap_multi_id': self.id,
                                                      'reason_code_id': self.reason_code_id.id})
                        move_box._action_done()

                        qty_diff_unit = abs(line.diff_qty)
                        move_unit = self.env['stock.move'].create({
                            'name': self.reason_code_id.name,
                            'location_id': line.dest_location_id.id,
                            'location_dest_id': line.src_location_id.id,
                            'product_id': line.product_template_id.product_variant_id.id if line.product_template_id.product_variant_id else False,
                            'product_uom': line.product_template_id.product_variant_id.uom_id.id if line.product_template_id.product_variant_id and line.product_template_id.product_variant_id.uom_id else False,
                            'product_uom_qty': qty_diff_unit,
                        })
                        move_unit.move_line_ids = False
                        move_unit._action_confirm()
                        move_unit._action_assign()
                        move_unit.move_line_ids.write(
                            {'qty_done': qty_diff_unit, 'scrap_multi_id': self.id, 'reason_code_id': self.reason_code_id.id})
                        move_unit._action_done()

                # raise UserError(_('UnBox')) 

            elif self.type_adjust in 'adjust':
                for line in self.order_line_ids:
                    move = self.env['stock.move'].create({
                        'name': self.reason_code_id.name,
                        'location_id': line.src_location_id.id,
                        'location_dest_id': line.dest_location_id.id,
                        'product_id': line.product_id.id,
                        'product_uom': line.uom_id.id,
                        'product_uom_qty': abs(line.diff_qty),
                    })
                    move.move_line_ids = False
                    move._action_confirm()
                    move._action_assign()
                    move.move_line_ids.write({'qty_done': abs(line.diff_qty), 'scrap_multi_id': self.id,
                                              'reason_code_id': self.reason_code_id.id})  # This creates a stock.move.line record. You could also do it manually
                    move._action_done()

            self.state = 'done'

    @api.depends('reason_code_id')
    def _compute_location(self):
        for rec in self:
            if rec.received_loss == 'loss':
                rec.src_location_id = self.env.user.company_id.location_id.id
                rec.dest_location_id = rec.reason_code_id.location_id.id
            else:
                rec.src_location_id = rec.reason_code_id.location_id.id
                rec.dest_location_id = self.env.user.company_id.location_id.id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('multi.scrap') or 'New'

        return super(MultiScrap, self).create(vals_list)


    @api.depends('state', 'order_line_ids')
    def _compute_show_confirm(self):
        for picking in self:
            if not picking.order_line_ids:
                picking.show_confirm = False
            elif picking.state == 'wait_to_approve':
                picking.show_confirm = True
            elif picking.state != 'wait_to_approve':
                picking.show_confirm = False
            else:
                picking.show_confirm = True

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def unlink(self):
        self.mapped('stock_move_ids').set_to_draft()
        self.with_context(prefetch_fields=False).mapped('stock_move_ids').unlink()  # Checks if moves are not done
        return super(MultiScrap, self).unlink()

    def set_to_draft(self):
        for stock in self.stock_move_ids:
            stock.state = 'cancel'
        for line in self.stock_move_line_ids:
            line.state = 'cancel'
        self.write({'state': 'wait_to_approve'})

        move_obj = self.env['stock.move']
        for pick in self:
            ids2 = [move.id for move in pick.stock_move_ids]
            moves = move_obj.browse(ids2)
            moves.sudo().action_draft()
            for move in moves:
                for m_line in move.move_line_ids:
                    m_line.unlink()
        return True

    @api.ondelete(at_uninstall=False)
    def _unlink_except_done(self):
        if 'done' in self.mapped('state'):
            raise UserError(_('You cannot delete when operation is done.'))

    # @api.onchange('location_adjust')
    # def _onchange_location_adjust(self):
    #     if self.location_adjust == 'fc':
    #         self.src_location_id = self.env.user.branch_id.location_id.id
    #         return {'domain': {'src_location_id': [('id', '=', self.env.user.branch_id.location_id.id)]}}
    #     else:
    #         self.branch_id = False
    #         self.src_location_id = False
    #         return {'domain': {'src_location_id': [('warehouse_id', 'in', self.env.user.warehouse_ids.ids)]}}
    #

class ScrapOrderLine(models.Model):
    _name = 'multi.scrap.line'
    _description = "Multi Scrap/Adjust Stock"

    # states={'done': [('readonly', True)]}, check_company=True
    # picking_id = fields.Many2one('multi.scrap', string='Picking')
    scrap_adjust_id = fields.Many2one('multi.scrap', string='Scrap Order')
    product_template_id = fields.Many2one('product.template', domain="[('type', 'in', ['consu']),('is_storable', '!=', False)]",
                                          string='Product Template', required=True)
    product_id = fields.Many2one('product.product', related='product_template_id.product_variant_id', string='Product')
    on_hand = fields.Float(compute='_compute_quantity', string='On Hand', store=True)
    old_on_hand = fields.Float(string='Old On Hand', store=True)
    product_barcode = fields.Char('Barcode', related='product_template_id.barcode')
    lot_id = fields.Many2one('stock.lot', string='Lot/Serial Number')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', related='product_template_id.uom_id')
    # product_id = fields.Many2one(
    #     'product.product', 'Product', domain="[('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", required=True, states={'done': [('readonly', True)]}, check_company=True)
    quantity = fields.Float(string='Quantity', required=True, digits='Product Unit of Measure')
    cost = fields.Float(related='product_template_id.standard_price', string='Cost Amount')
    sale_price = fields.Float(related='product_template_id.list_price', string='Sale Price')
    stock_value = fields.Float(compute='_compute_stock_value', string='Count Amount')
    diff_qty = fields.Float(string='Diff Qty')
    diff_amount = fields.Float(compute='_compute_stock_value', string='Diff Amount')
    reason_code_id = fields.Many2one(related='scrap_adjust_id.reason_code_id', string='Reason Code')
    src_location_id = fields.Many2one('stock.location', compute='_compute_location', string='Source Location')
    dest_location_id = fields.Many2one('stock.location', compute='_compute_location', string='Dest Location')
    type_adjust = fields.Selection(related='scrap_adjust_id.type_adjust', string='Type Ajust', store=True)
    state = fields.Selection(related='scrap_adjust_id.state', string="State", store=True)
    # move_id = fields.Many2one('stock.move', 'Scrap Move', readonly=True, check_company=True, copy=False)
    package_id = fields.Many2one('stock.quant.package', string='Package')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record.old_on_hand = record.on_hand

        return records

    def write(self, values):
        adjust = super(ScrapOrderLine, self).write(values)
        return adjust

    # @api.onchange('product_id','product_template_id')
    # def _onchange_product_id(self):
    #     self.old_on_hand = self.on_hand

    @api.onchange('product_template_id', 'quantity', 'diff_qty')
    def _onchange_diff_qty(self):
        self.old_on_hand = self.on_hand
        if self.type_adjust not in ['scrap']:
            self.diff_qty = self.quantity - self.old_on_hand

    @api.depends('quantity', 'diff_qty')
    def _compute_stock_value(self):
        for rec in self:
            rec.stock_value = rec.quantity * rec.product_id.standard_price
            # if rec.type_adjust == 'adjust':
            #     rec.diff_qty = rec.quantity - rec.old_on_hand
            rec.diff_amount = rec.diff_qty * rec.product_id.standard_price

    @api.depends('reason_code_id', 'quantity')
    def _compute_location(self):
        for rec in self:
            if rec.diff_qty < 0:
                rec.src_location_id = rec.scrap_adjust_id.src_location_id.id
                rec.dest_location_id = rec.scrap_adjust_id.dest_location_id.id
            else:
                rec.src_location_id = rec.scrap_adjust_id.dest_location_id.id
                rec.dest_location_id = rec.scrap_adjust_id.src_location_id.id

    @api.depends('product_template_id', 'lot_id')
    def _compute_quantity(self):
        for rec in self:
            if rec.src_location_id.usage == 'internal':
                stock_quant = self.env['stock.quant'].search(
                    [('product_id', '=', rec.product_id.id), ('location_id', '=', rec.src_location_id.id)])
            else:
                stock_quant = self.env['stock.quant'].search(
                    [('product_id', '=', rec.product_id.id), ('location_id', '=', rec.dest_location_id.id)])

            # if rec.scrap_adjust_id.received_loss == 'loss':
            #     # stock_quant = self.env['stock.quant'].search([('product_id','=',rec.product_id.id),('location_id','=',rec.src_location_id.id),'|',('lot_id','=',rec.lot_id.id),('lot_id','=',False)])
            #     stock_quant = self.env['stock.quant'].search([('product_id','=',rec.product_id.id),('location_id','=',rec.src_location_id.id)])
            # else:
            #     # stock_quant = self.env['stock.quant'].search([('product_id','=',rec.product_id.id),('location_id','=',rec.dest_location_id.id),'|',('lot_id','=',rec.lot_id.id),('lot_id','=',False)])
            #     stock_quant = self.env['stock.quant'].search([('product_id','=',rec.product_id.id),('location_id','=',rec.dest_location_id.id)])

            on_hand = 0
            for quant in stock_quant:
                on_hand += quant.quantity
            rec.on_hand = on_hand

    def show_stock_quantity(self):
        return {
            'name': _('Quantity On Hand'),
            'view_mode': 'tree',
            'res_model': 'stock.quant',
            'view_id': self.env.ref('stock.view_stock_quant_tree_inventory_editable').id,
            'type': 'ir.actions.act_window',
            'domain': [('product_id', '=', self.product_id.id), ('location_id', '=', self.src_location_id.id)]
        }


class Product(models.Model):
    _inherit = 'product.product'

    scrap_location_id = fields.Many2one(
        'stock.location', string='Scrap Location')


class StockMove(models.Model):
    _inherit = 'stock.move'

    scrap_multi_id = fields.Many2one('multi.scrap', string='Multi Scrap')
    reason_code_id = fields.Many2one("scrap.reason.code", string="Reason code")

    def action_draft(self):
        res = self.write({'state': 'draft'})
        return res


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    scrap_multi_id = fields.Many2one('multi.scrap', string='Multi Scrap')
    reason_code_id = fields.Many2one("scrap.reason.code", string="Reason code")
