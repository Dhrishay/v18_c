# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2020 - Today O4ODOO (Omal Bastin)
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    backorder_location_id = fields.Many2one(
        "stock.location", string="Backorder Location", related="company_id.backorder_location_id",
        readonly=False, help="Location where the backorder will be created.", store=True
    )
    
    is_confirm_mapping = fields.Boolean(string="Confirm Mapping",related="company_id.is_confirm_mapping", store=True, readonly=False)

    is_receipt_lock_destination_location = fields.Boolean(
        string="Receipt : Lock Destination Location",
        help="If checked, the destination location will be locked and the user will not be able to change it.",
        related="company_id.is_receipt_lock_destination_location", store=True, readonly=False
    )

    is_delivery_lock_src_location = fields.Boolean(
        string="Delivery : Lock Source Location",
        help="If checked, the destination location will be locked and the user will not be able to change it.",
        related="company_id.is_delivery_lock_src_location", store=True, readonly=False
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_receipt_lock_destination_location = fields.Boolean(
        string="Receipt:Lock Destination Location"
    )
    is_delivery_lock_src_location = fields.Boolean(
        string="Delivery:Lock Destination Location"
    )
    backorder_location_id = fields.Many2one(
        "stock.location", string="Backorder Location", help="Location where the backorder will be created."
    )
    is_confirm_mapping = fields.Boolean(string="Confirm Mapping", default=False)


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    location_id = fields.Many2one(
        "stock.location", string="Backorder Location",
        default=lambda self:self.env.company.backorder_location_id,
    )

    @api.model
    def _default_picking_type(self):
        """ When active_model is res.partner, the current partners should be attendees """
        if self._context.get('button_validate_picking_ids', False):
            res = self.env['stock.picking'].browse(self._context.get('button_validate_picking_ids'))
            if res and res[0].picking_type_code == 'incoming':
                return True
        return False

    picking_incoming = fields.Boolean(default=_default_picking_type)

    def process(self):
        new_context = dict(self.env.context)
        if self.pick_ids and self.pick_ids[0].picking_type_code == 'incoming':
            new_context.update({
                'backorder_location': self.location_id and self.location_id.id or False,
            })
            self = self.with_context(new_context)
        return super(StockBackorderConfirmation, self).process()


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_lock_receipt = fields.Boolean(
        string="Lock Receipt",related='company_id.is_receipt_lock_destination_location',
        store=True
    )
    is_lock_delivery = fields.Boolean(
        string="Lock Delivery",
        related='company_id.is_delivery_lock_src_location', store=True
    )

    def _create_backorder(self, backorder_moves=None):
        pickings_to_detach = super(StockPicking, self)._create_backorder(backorder_moves)
        if pickings_to_detach and self.company_id.backorder_location_id:
            pickings_to_detach.location_dest_id = self.company_id.backorder_location_id.id
        return pickings_to_detach

    def _prepare_stock_move_vals(self, first_line, order_lines):
        res = super()._prepare_stock_move_vals(first_line, order_lines)
        if first_line:
            res.update({
                'pos_session_id': first_line.order_id and first_line.order_id.session_id and first_line.order_id.session_id.id or False,
                'pos_order_id': first_line.order_id and first_line.order_id.id or False,
            })
        return res
    
     
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        # Add condition here for the receives Product only when destination location is not locked.    
        for rec in self:
            for line in rec.move_line_ids_without_package:
                if (rec.picking_type_id.default_location_dest_id and 
                    rec.picking_type_id.is_lock_location and 
                    line.location_dest_id and
                    line.location_dest_id.id == rec.picking_type_id.default_location_dest_id.id):
                    raise ValidationError(_("You must set Destination Location."))
                if line.location_dest_id and line.location_id and line.location_dest_id.id == line.location_id.id:
                    raise ValidationError(_("You must set Different Source or Destination Location."))
        return res


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    is_lock_receipt = fields.Boolean(
        string="Lock Receipt", related='company_id.is_receipt_lock_destination_location',
        store=True
    )
    is_lock_delivery = fields.Boolean(
        string="Lock Delivery", related='company_id.is_delivery_lock_src_location',
        store=True
    )


class StockPutawayRule(models.Model):
    _inherit = 'stock.putaway.rule'
    
    location_out_id = fields.Many2one(
        'stock.location', domain=False)


class StockMove(models.Model):
    _inherit = 'stock.move'

    pos_session_id = fields.Many2one('pos.session', index=True)
    pos_order_id = fields.Many2one('pos.order', index=True)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(StockMove, self).create(vals_list)
        for re in res:
            if re.picking_id.picking_type_code in ['incoming', 'outgoing'] and not (re.pos_order_id or re.pos_session_id):
                if not (re.purchase_line_id or re.sale_line_id or re.picking_id.product_markdown_id):
                    raise UserError(_('You cannot create another line from a sale or purchase.'))
        return res

    
    def _split(self, qty, restrict_partner_id=False):
        
        res = super(StockMove, self)._split(qty, restrict_partner_id)
        for re in res:
            backorder_location = self.company_id.backorder_location_id.id
            if backorder_location:
                re['location_dest_id'] = backorder_location
        return res
