from odoo import models, fields, _
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')

class CreateCustomerWizard(models.TransientModel):
    _name = 'create.customer.wizard'
    _description = 'Create Customer Wizard'

    rental_space_ids = fields.Many2many('rental.space', string='Rental Space')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    # contract_type = fields.Selection ([('days','Days'),('month','Month')], string='Contract type' , required=True)
    contract_type = fields.Selection(related='location_id.contract_type', string='Contract Type', readonly=True, store=True, )
    remark_id = fields.Text(string="Remark", required=True)
    days_values = fields.Char(string='Number of Days',help="Enter a of numbers (1 - 31).")

    location_types = fields.Many2one('rental.type.all', string="Location Types", required=False)
    location_id = fields.Many2one('rental.type.all.line', string="Location", required=False)
    rental_area_size = fields.Char(related='location_id.size_lines', string='Size', required=True)
    agreed_amount = fields.Monetary(related='location_id.agreed_amounts',string="Amount", currency_field="currency_id")
    currency_id = fields.Many2one('res.currency', related='location_types.currency_id', string="Currency", domain=[('name', 'in', ['USD', 'LAK', 'THB'])])
    image = fields.Image(related='location_types.image', string="Image", required=True)
    # location_branch_id = fields.Char(related='location_id.location_branch_id', string='Location Branch', required=True)
    location_branch_id = fields.Many2one(related='location_id.location_branch_id', string='Location Branch', required=True)

    def action_sale(self):
        """Create a single Sale Order with multiple lines for each selected rental space."""
        SaleOrder = self.env['sale.order']
        SaleOrderLine = self.env['sale.order.line']

        # Check for a partner and rental space
        if not self.partner_id:
            raise UserError(_("Please select a customer."))
        if not self.rental_space_ids:
            raise UserError(_("Please select one or more rental spaces to create an offer."))
        if not self.image:
            raise UserError(_("Rental space has no image assigned!"))
        
        # Check if any of the selected rental spaces have 'occupied' or 'booking' state
        for rental_space in self.rental_space_ids:
            if rental_space.state in ['occupied', 'booking']:
                raise UserError(_("Cannot create a quote for a region with status '%s'") % rental_space.state)

        # Get or create UoM for "Days"
        uom_day = self.env.ref('uom.product_uom_day', raise_if_not_found=False)
        uom_month = self.env.ref('uom.product_uom_month', raise_if_not_found=False)

        if not uom_day:
            uom_day = self.env['uom.uom'].search([('name', '=', 'Days')], limit=1)
            if not uom_day:
                uom_category = self.env['uom.category'].search([('name', '=', 'Time')], limit=1)
                uom_day = self.env['uom.uom'].create({
                    'name': 'Days',
                    'category_id': uom_category.id if uom_category else 1,
                    'uom_type': 'reference',
                    'rounding': 1.0,
                })
        if not uom_month:
            uom_month = self.env['uom.uom'].search([('name', '=', 'Month')], limit=1)
            if not uom_month:
                uom_category = self.env['uom.category'].search([('name', '=', 'Time')], limit=1)
                uom_month = self.env['uom.uom'].create({
                    'name': 'Month',
                    'category_id': uom_category.id if uom_category else 1,
                    'uom_type': 'reference',
                    'rounding': 1.0,
                })

        rental_product = self.env.ref('lod_rental_space.product_rental_space', raise_if_not_found=False)
        if not rental_product:
            rental_product = self.env['product.product'].search([('name', '=', 'Rental Space Service')], limit=1)
            if self.contract_type == 'days' and rental_product.uom_id != uom_day:
                 rental_product.write({'uom_id': uom_day.id, 'uom_po_id': uom_day.id})
            elif self.contract_type == 'month' and rental_product.uom_id != uom_month:
                 rental_product.write({'uom_id': uom_month.id, 'uom_po_id': uom_month.id})

        # ดึง Pricelist จาก rental_space_ids
        pricelist_id = None
        for rental_space in self.rental_space_ids:
            if not rental_space.location_types or not rental_space.location_types.prieclist:
                raise UserError(_("Rental Space '%s' is missing a Pricelist.") % rental_space.name)
            if not pricelist_id:
                pricelist_id = rental_space.location_types.prieclist.id
            elif pricelist_id != rental_space.location_types.prieclist.id:
                raise UserError(_("Rental Spaces must share the same Pricelist."))



        # Create a single sale order for all rental spaces
            sale_order_vals = {
            'partner_id': self.partner_id.id,
            'date_order': fields.Datetime.now(),
            'origin': ', '.join(rental.name for rental in self.rental_space_ids),
            'rental_space_id': self.rental_space_ids[0].id,
            'pricelist_id': pricelist_id,  # เพิ่ม Pricelist ใน Sale Order
            'image': self.image,
        }
        sale_order = SaleOrder.create(sale_order_vals)
        self.rental_space_ids.order_id = sale_order.id

        for rental_space in self.rental_space_ids:
            if not rental_space.agreed_amount:
                raise UserError(_("Lost Amount for Leased Space '%s'." % rental_space.name))
            if self.contract_type == 'days':
                product_uom_qty = self.days_values  
            else:
                product_uom_qty = 1  

            remark_name = self.remark_id or rental_space.name

            # Create sale order line for each rental space
            sale_order_line_vals = {
                'order_id': sale_order.id,
                'product_id': rental_product.id,
                'name': self.remark_id or rental_space.name,
                'product_uom_qty': product_uom_qty,
                'product_uom': rental_product.uom_id.id,
                'price_unit': rental_space.agreed_amount,
                'lct_id': rental_space.location_id.location_lines if rental_space.location_id else "",
                'size_id': rental_space.rental_area_size if rental_space.rental_area_size else "",
                'pricelist_id': pricelist_id,  # เพิ่ม Pricelist ใน Sale Order Line
                'location_branch_id': rental_space.location_branch_id if rental_space.location_branch_id else "",
            }
            SaleOrderLine.create(sale_order_line_vals)

            # Update the state and partner_id in rental space
            rental_space.write({'partner_id': self.partner_id.id, 'state': 'booking'})
            rental_space.write({'contract_type': self.contract_type})
            rental_space.write({'days_values': self.days_values})
            rental_space.write({'remark_id': self.remark_id})

            _logger.debug(f"Created sale order line for rental space '{rental_space.name}' with agreed amount {rental_space.agreed_amount}")
            _logger.info("Image successfully saved in Sale Order: %s", sale_order.image)

        # Return action to show the created sale order
        return {
            'type': 'ir.actions.act_window',
            'name': _('Created Sale Order'),
            'res_model': 'sale.order',
            'view_mode': 'form',
            'view_id': self.env.ref('lod_rental_space.sale_order_two_action_form').id, 
            'res_id': sale_order.id,
            'target': 'current',
        }
        
       