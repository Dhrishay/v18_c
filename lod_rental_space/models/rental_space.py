from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class RentalPartner(models.Model):
    _inherit = 'res.partner'

    rental_space_id = fields.Many2one('rental.space', string='Rental Space', readonly=True, ondelete='set null')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    # Define the billboard_id field as a Many2one relationship with rental.space
    billboard_id = fields.Many2one('rental.space', string="Billboard")
    location_id = fields.Many2one('rental.type.all.line', string="Location", required=False)
    lct_id =  fields.Char(string="Location ", readonly=True)
    size_id =  fields.Char(string="Size", readonly=True)
    location_branch_id = fields.Char( string='Location Branch', required=False)

   

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    rental_space_id = fields.Many2one('rental.space', string='Rental Space ID', readonly=True)
    image = fields.Image(string="Sale Order Image")

    owner_image = fields.Image(string="Owner Image")
    owner_text_header = fields.Html(string="Owner Text Header", translate=True,)
    owner_text_footer = fields.Html(string="Owner Text Footer", translate=True,)

    contract_image_id = fields.Image(string="Owner Contract Image")
    contract_header_id = fields.Html(string="Owner Contract Header", translate=True,)
    text_id = fields.Html(string="Terms Template", translate=True,)

    
    def action_create_agreement_bill(self):
        """Creates a billboard rental agreement associated with the sale order."""
        for rec in self:
            rec.state = "sale"

            # Check or create rental products
            rental_product = self.env.ref('lod_rental_space.product_rental_space', raise_if_not_found=False)
            if not rental_product:
                rental_product = self.env['product.product'].search([('name', '=', 'Rental Space Service')], limit=1)

            list_item = []
            for line in rec.order_line:
                lines = {
                    'billboard_id': line.name,
                    'location_branch_id': line.location_branch_id,
                    'rental_area_sizes': line.size_id,
                    'location_ids': line.lct_id,
                    'product_uom_qty': line.product_uom_qty or 0.0,
                    'product_uom': line.product_uom.name,
                    'price_unit': line.price_subtotal,
                    'discount': line.discount,
                    # 'agreed_amount': line.price_subtotal or 0.0,
                   
                }
                list_item.append((0, 0, lines))
            
            contract_type = self.env['agreement.contract.type'].search([], limit=1)
            contract_type_id = contract_type.id if contract_type else None 

            billing_cycle = self.env['agreement.cycle'].search([], limit=1)
            cycle_id = billing_cycle.id if billing_cycle else None 

            agreement_billboard = self.env['agreement.billboard'].create({
                'partner_id': rec.partner_id.id,
                'quotation_rfe': rec.id,
                'date_agreement': fields.Date.today(),
                'argreement_line_ids': list_item,
                'product_id': rental_product.id,
                'contract_type_id': contract_type_id, 
                'cycle_id': cycle_id,
                'currency_id': rec.pricelist_id.currency_id.id,  # Include pricelist currency
                'pricelist_id': rec.pricelist_id.id, 

                'contract_image_id': rec.contract_image_id,
                'contract_header_id': rec.contract_header_id,
                'text_id': rec.text_id,
               
            })

            if hasattr(rec, 'agreement_billboard_id'):
                rec.agreement_billboard_id = agreement_billboard.id

        return {
            'name': 'Rental Space Agreement',
            'type': 'ir.actions.act_window',
            'res_model': 'agreement.billboard',
            'view_mode': 'form',
            'res_id': agreement_billboard.id,
            'target': 'current',
        }




class RentalSpace(models.Model):
    _name = "rental.space"
    _description = "Rental Space"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "name"
    # _rec_name = 'location_types'

    name = fields.Char(string='Name', index=True, required=True, copy=False)
    state = fields.Selection([
        ('available', 'Available'),
        ('booking', 'Booking'),
        ('occupied', 'Occupied'),
        ('done', 'Done')
    ], default="available", readonly=True, string='Status')
    
    partner_id = fields.Many2one('res.partner', string='Customer',)
    agreement_id = fields.Many2one('agreement.billboard', readonly=True, string='Contract')
    user_id = fields.Many2one('res.users', string='Responsible')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    note = fields.Text(string='Notes') 

    owner_tag_id = fields.Many2one('owner.tag', string="Owner", required=True)
    owner_image = fields.Image(related='owner_tag_id.owner_image', string="Owner Image")
    owner_text_header = fields.Html(related='owner_tag_id.owner_text_header', string="Owner Text Header", translate=True,)
    owner_text_footer = fields.Html(related='owner_tag_id.owner_text_footer', string="Owner Text Footer", translate=True,)

    contract_image_id = fields.Image(related='owner_tag_id.contract_image_id', string="Owner Contract Image")
    contract_header_id = fields.Html(related='owner_tag_id.contract_header_id', string="Owner Contract Header", translate=True,)

    # contract_template_id = fields.Many2one('agreement.terms.template', string="Agreement Terms Template", required=True)
    contract_template_id = fields.Many2one('agreement.terms.template', string="Agreement Terms Template", 
                                           required=True, default=lambda self: self.env['agreement.terms.template'].search([], limit=1).id or False)
    text_id = fields.Html(related='contract_template_id.text_id', string="Terms Template", translate=True,)

    location_types = fields.Many2one('rental.type.all', string="Location Types", required=True)
    location_id = fields.Many2one('rental.type.all.line', string="Location", required=True)
    rental_area_size = fields.Char(related='location_id.size_lines', string='Size', required=True)
    agreed_amount = fields.Monetary(related='location_id.agreed_amounts',string="Amount", currency_field="currency_id")
    currency_id = fields.Many2one('res.currency', related='location_types.currency_id', string="Currency", domain=[('name', 'in', ['USD', 'LAK', 'THB'])])
    image = fields.Image(related='location_types.image', string="Image", required=True)
    location_branch_id = fields.Many2one(related='location_id.location_branch_id', string='Location Branch', required=True)
    contract_type = fields.Selection(related='location_id.contract_type', string='Contract Type', readonly=True, store=True, )
   
    order_id = fields.Many2one('sale.order', string='Order')
    remark_id = fields.Text(string="Remark")
    days_values = fields.Char(string='Number of Days',help="Enter a of numbers (1 - 29).")
    rental_count_customer_sale = fields.Integer(compute='_compute_rental_count_customer_sale', string="Customer Invoices")

    @api.onchange('location_types', 'location_id')
    def _onchange_location_fields(self):
        """
        Update contract_type based on the selected location_types or location_id.
        """
        if self.location_types:
            self.contract_type = self.location_types.contract_type
        else:
            self.contract_type = False

    @api.constrains('days_values')
    def _validate_days_values(self):
        for record in self:
            if record.days_values:
                values = record.days_values.split(',')
                for value in values:
                    value = value.strip() 
                    if not value.isdigit() or not (1 <= int(value) <= 29):
                        raise ValidationError(
                            "Each number must be between 1 and 29")
   
    def _compute_rental_count_customer_sale(self):
        for rec in self:
           sale_count = self.env['sale.order'].search_count([('rental_space_id', '=', rec.id)])
           rec.rental_count_customer_sale = sale_count

    def smart_button_sale(self):
        action = self.env.ref('lod_rental_space.sale_order_two_action').read()[0]
        # Update the domain to filter only records related to the current rental space
        action['domain'] = [('rental_space_id', '=', self.id)]
        action['context'] = dict(self.env.context, default_rental_space_id=self.id)
        return action
    
    #  smart button 
  
   
    def create_sale_orders(self):
        if not self.partner_id:
            raise UserError(_("ກະລຸນາເພີ່ມຂໍ້ມູນລູກຄ້າກ່ອນ!!"))
        
        if not self.remark_id:
            raise UserError(_("ກະລຸນາເພີ່ມລາຍລະອຽດການເຊົ່າກ່ອນ (Remark)!!"))
        
        if not self.image:
            raise UserError(_("Rental space has no image assigned!"))
            
        """ Function to create Sale Order from Rental Space and open it upon success. """
        sale_order_obj = self.env['sale.order']
        sale_order_line_obj = self.env['sale.order.line']

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

        for record in self:
            # if not record.owner_ids:
            #     raise UserError(_("Owner is missing for Rental Space '%s'.") % record.name)
            if not record.agreed_amount:
                raise UserError(_("Agreed amount is missing for Rental Space '%s'.") % record.name)
            # if not record.location_id or not record.rental_area_size or not record.location_types:
            #     raise UserError(_("Location or Rental Area Size is missing for Rental Space '%s'.") % record.name)

        
            sale_order_vals = {
                'partner_id': record.partner_id.id,
                'rental_space_id': record.id,
                'date_order': fields.Datetime.now(),
                'origin': record.name,
                'user_id': record.user_id.id or self.env.uid,
                'pricelist_id': record.location_types.prieclist.id,
                'image': record.image,
                # 'owner_image': record.owner_image,
                'owner_image': record.owner_tag_id.owner_image,
                'owner_text_header': record.owner_text_header,
                'owner_text_footer': record.owner_text_footer,

                'contract_image_id': record.owner_tag_id.contract_image_id,
                'contract_header_id': record.contract_header_id,
                'text_id': record.text_id,
            }
            sale_order = sale_order_obj.create(sale_order_vals)
            record.order_id = sale_order.id

            # print('=====owner_text_header=======',sale_order_vals.owner_text_header)
            # product_uom_qty = record.days_values if self.contract_type == 'days' else 1

            if self.contract_type == 'days':
                product_uom_qty = record.days_values  
            else:
                product_uom_qty = 1  

            sale_order_line_vals = {
                'order_id': sale_order.id,
                'product_id': rental_product.id,
                'name': record.remark_id,
                'product_uom_qty': product_uom_qty,
                'product_uom': rental_product.uom_id.id,
                'price_unit': record.agreed_amount,
                'lct_id': record.location_id.location_lines,
                'size_id': record.rental_area_size,
                'location_branch_id': record.location_branch_id.name,
            }
            sale_order_line_obj.create(sale_order_line_vals)

            # Update State to "booking"
            record.state = "booking"

            _logger.info("Image successfully saved in Sale Order: %s", sale_order.image)

        # Return action to open the created Sale Order
        return {
            'name': _('Sale Order for %s') % record.partner_id.name,
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'view_id': self.env.ref('lod_rental_space.sale_order_two_action_form').id,  
            'res_id': sale_order.id,
            'target': 'current',
        }
    
    def action_window_open(self):
        context = self._context
        active_ids = context.get('active_ids')
        action = {
            'name': 'Create Sale Order Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'create.customer.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('lod_rental_space.view_create_customer_form').id,
            'target': 'new',
            'context': {'default_rental_space_ids': active_ids}
        }
        return action
