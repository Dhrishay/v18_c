from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from math import ceil
import logging


_logger = logging.getLogger(__name__)

class RentalSpaceAgreement(models.Model):
    _name = "agreement.billboard"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Agreement"
    _order = "name"

    # name = fields.Char(string='Reference', index=True, default='KKM/', copy=False, required=True, readonly=True)
    name = fields.Char(
        string='Reference',
        index=True,
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('agreement.billboard') or _('New')
    )
    
    product_id = fields.Many2one('product.product', string='Product', required=True)
    
    quotation_rfe = fields.Many2one('sale.order', string='Quotation RFE', readonly=True)
    date_agreement = fields.Date(string='Start Date', default=fields.Date.today, copy=False, readonly=False)

    contract_type_id = fields.Many2one('agreement.contract.type', string='Contract Type', required=True)
    cycle_id = fields.Many2one('agreement.cycle', string='Billing Cycle', required=True)

    invoice_date = fields.Date(string='Invoice Date', readonly=False)
    final_date = fields.Date(string="End Date", copy=False, readonly=False)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    partner_img = fields.Binary("Image", related='partner_id.image_1920',readonly=True)
    street_partner = fields.Char(related='partner_id.street', string='Village',readonly=True)
    city_partner = fields.Char(related='partner_id.city', string='District',readonly=True)
    stade_partner = fields.Char(related='partner_id.state_id.name', string='Province',readonly=True)
    phone_partner = fields.Char(related='partner_id.phone', string='Phone',readonly=True)
    mobile_partner = fields.Char(related='partner_id.mobile', string='Mobile',readonly=True)
    email_partner = fields.Char(related='partner_id.email', string='Email',readonly=True)
    user_id = fields.Many2one('res.users',default=lambda self: self.env.user, string='Responsible', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'In Progress'),
        ('closed', 'Terminated'),
        ('cancel', 'Cancel'),], 
        string='Status', index=True, readonly=True, default='draft', copy=False,)
    agreement_billboard_note = fields.Char(string="Notes")
    agree_count_customer_invoice = fields.Integer(compute='_agreement_count_customer_invoice', string="Customer Invoices")
    argreement_line_ids = fields.One2many('agreement.billboard.lines', 'argreement_id', string='Argreement Line')
    billboard_id = fields.Many2one('rental.space', string="Billboard")
    remark_id = fields.Text(string="Remark")
    owner_tag_id = fields.Many2many('owner.tag', string="Owner")
    days_values = fields.Char(string='Number of Days',help="Enter a of numbers (1 - 31).")
    currency_id = fields.Many2one('res.currency', string="Currency", domain=[('name', 'in', ['USD', 'LAK', 'THB'])])
    pricelist_id = fields.Many2one( 'product.pricelist',  string='Pricelist')

    contract_image_id = fields.Image( string="Owner Contract Image")
    contract_header_id = fields.Html( string="Owner Contract Header", translate=True,)
    text_id = fields.Html(string="Terms Template", translate=True,)

    # note_header = fields.Html('agreement.terms.template', string="Note", default="")
    
    # terms_template_id = fields.Many2one(
    #     'agreement.terms.template', 
    #     string="Terms Template",
    #     help="Select a template to apply to this agreement."
    # )

    # text_id = fields.Html(
    #     string="Note",
    #     compute="_compute_text_id",
    #     store=True
    # )

    # @api.depends('terms_template_id')
    # def _compute_text_id(self):
    #     for record in self:
    #         record.text_id = record.terms_template_id.text_id if record.terms_template_id else ""

    # @api.onchange('terms_template_id')
    # def _onchange_terms_template(self):
    #     """ When terms_template_id is selected, update text_id with template content """
    #     if self.terms_template_id:
    #         self.text_id = self.terms_template_id.text_id



    # invoice_ids = fields.One2many('account.move', 'agreement_id', string='Invoices')  # Link to invoices

    # Define the total_amount field as a computed field
    total_amount = fields.Float( string="Total Amount", compute='_compute_total_amount', store=True)
       
    ### Activity 15 days and 7 days #### 
    @api.model_create_multi
    def create(self, vals):
        record = super(RentalSpaceAgreement, self).create(vals)
        record._schedule_reminder_activity()  
        return record
    
    def write(self, vals):
        res = super(RentalSpaceAgreement, self).write(vals)
        if 'final_date' in vals or 'state' in vals:  
            self._handle_state_and_reminders(vals)
        return res
    
    ### **📌 Delete or create alert when `state` changes**
    def _handle_state_and_reminders(self, vals):
        """ จัดการ state และ reminder """
        for record in self:
            if vals.get('state') in ['closed', 'cancel']:
                activities = self.env['mail.activity'].search([
                    ('res_model', '=', 'agreement.billboard'),
                    ('res_id', '=', record.id),
                ])
                if activities:
                    activities.unlink()  # Delete all related notifications immediately.
            else:
                record._schedule_reminder_activity()

    def _schedule_reminder_activity(self):
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        today = fields.Date.context_today(self)
            
        for record in self:
            reminder_dates = [
                record.final_date - timedelta(days=15),
                record.final_date - timedelta(days=7)
            ]
            existing_activities = self.env['mail.activity'].sudo().search([
                ('res_model', '=', 'agreement.billboard'),
                ('res_id', '=', record.id),
                ('activity_type_id', '=', activity_type.id),
            ])
            for reminder_date in reminder_dates:
                self.env['mail.activity'].create({
                    'res_model': 'agreement.billboard',
                    'res_model_id': self.env['ir.model']._get('agreement.billboard').id,
                    'res_id': record.id,
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': _('Reminder: Agreement Due Soon'),
                    'note': _('The agreement is due on %s. Please take necessary action.') % record.final_date.strftime('%d/%m/%Y'),
                    'user_id': record.user_id.id or self.env.user.id,
                    'date_deadline': reminder_date,  # ✅ Use single values, not lists.
    })

    @api.model_create_multi
    def create(self, vals):
        vals['name']= self.env['ir.sequence'].next_by_code('agreement.billboard')
        return super(RentalSpaceAgreement, self).create(vals)
    
    @api.onchange('contract_type_id', 'date_agreement')
    def _onchange_contract_type_id(self):
        if self.contract_type_id and self.date_agreement:
            try:
                calculated_date = self.date_agreement + relativedelta(months=self.contract_type_id.sum_month)
                self.final_date = calculated_date - timedelta(days=1)
            except Exception as e:
                self.final_date = False 
   
    @api.onchange('contract_type_id')
    def _onchange_contract_type_id(self):
        """
        Create or update Agreement Line and calculate agreed_amount = product_uom_qty * price_unit
        """
        if self.contract_type_id:
            contract_type_num = self.contract_type_id.sum_month

            if self.date_agreement:
                self.final_date = self.date_agreement + relativedelta(months=contract_type_num) - timedelta(days=1)

            # Update or create argreement_line_ids
            if self.argreement_line_ids:
                self.argreement_line_ids[0].product_uom_qty = contract_type_num
                
            # Update product_uom_qty values ​​and calculate agreed_amount for all lines in argreement_line_ids
            if self.argreement_line_ids:
                for line in self.argreement_line_ids:
                    try:
                        # Check and convert the value to float
                        product_uom_qty = float(line.product_uom_qty or 0.0)
                        price_unit = float(line.price_unit or 0.0)

                        line.product_uom_qty = contract_type_num
                        line.agreed_amount = product_uom_qty * price_unit

                    except (ValueError, TypeError) as e:
                        _logger.info('Error updating line "%s": %s', line.id, e)
                        line.agreed_amount = 0.0  
            else:
                # Create a new line if there is no data in argreement_line_ids
                self.argreement_line_ids = [(0, 0, {
                    'billboard_id': "Default Billboard",
                    'location_branch_id': "Default Location Branch",
                    'rental_area_sizes': "Default Size",
                    'location_ids': "Default Location",
                    'product_id': "Default Product",
                    'product_uom_qty': contract_type_num,  
                    'price_unit': 0.0,
                    'agreed_amount': 0.0,
                    'discount': 0.0,
                })]

            # Forced calculation agreed_amount
            for record in self.argreement_line_ids:
                try:
                    product_uom_qty = float(record.product_uom_qty or 0.0)
                    price_unit = float(record.price_unit or 0.0)
                    record.agreed_amount = product_uom_qty * price_unit
                except (ValueError, TypeError) as e:
                    _logger.info('Error processing record %s or New Record %s', record.id, e)
                    record.agreed_amount = 0.0
        else:
            _logger.info('No contract_type_id selected')

    
    @api.model_create_multi
    def create(self, vals):
        agreement = super(RentalSpaceAgreement, self).create(vals)
        agreement._update_agreement_lines()
        return agreement

    def write(self, vals):
        result = super(RentalSpaceAgreement, self).write(vals)
        if 'contract_type_id' in vals or 'date_agreement' in vals:
            self._update_agreement_lines()
        return result

    def _update_agreement_lines(self):
        # Ensure that agreed_amount in agreement lines is updated based on the contract type.
        for agreement in self:
            contract_months = agreement.contract_type_id.sum_month if agreement.contract_type_id else 0

            if contract_months and agreement.date_agreement:
                agreement.final_date = agreement.date_agreement + relativedelta(months=contract_months) - timedelta(days=1)

            line_updates = []
            for line in agreement.argreement_line_ids:
                try:
                    product_uom_qty = float(line.product_uom_qty or 0.0)  
                    price_unit = float(line.price_unit or 0.0)          
                    agreed_amount = product_uom_qty * price_unit         
                except (ValueError, TypeError):
                    raise UserError("Product quantity or price unit must be numeric.")

                line_updates.append((1, line.id, {
                    'product_uom_qty': product_uom_qty,
                    'price_unit': price_unit,
                    'agreed_amount': agreed_amount,
                }))

            if not line_updates:
                line_updates.append((0, 0, {
                    'billboard_id': "Default Billboard",
                    'location_branch_id': "Default Location Branch",
                    'rental_area_sizes': "Default Size",
                    'location_ids': "Default Location",
                    'product_id': "Default Product",
                    'product_uom_qty': contract_months,
                    'price_unit': 0.0,
                    'agreed_amount': 0.0,
                    
                }))

            agreement.argreement_line_ids = line_updates

    # Compute method to calculate total_amount
    @api.depends('argreement_line_ids.agreed_amount')
    def _compute_total_amount(self):
        for agreement in self:
            agreement.total_amount = sum(line.agreed_amount for line in agreement.argreement_line_ids)
    
    
    def contract_open(self):
        rental_id = self.env['rental.space'].search([('order_id', '=', self.quotation_rfe.id)])
        rental_id.start_date = self.date_agreement
        rental_id.end_date = self.final_date
        rental_id.agreement_id = self.id
        rental_id.user_id = self.user_id.id
        rental_id.state = 'occupied'
        self.state = 'open'
        self._schedule_reminder_activity()
        invoice_action = self.action_create_invoice()
        return invoice_action

    def action_create_invoice(self):
        if self.state != 'open':
            raise UserError("You can only create an invoice for agreements that are in the 'open' state.")
        
        contract_type_num = self.contract_type_id.sum_month
        cycle_num = self.cycle_id.sum_month
        total_amount = self.total_amount

        # Calculate the number of payment cycles
        month_of_payment = contract_type_num / cycle_num
        if month_of_payment % 1 != 0:
            raise UserError(_('Contract duration and cycle length must result in an integer number of payments.'))
        
        month_of_payment = int(month_of_payment)  

        # Calculate the base amount for each cycle
        base_amount_per_cycle = round(total_amount / month_of_payment, 2)
        payment_amounts = [base_amount_per_cycle] * month_of_payment

        # Adjust the last payment to fix rounding discrepancies
        payment_amounts[-1] = total_amount - sum(payment_amounts[:-1])

        duedate = self.date_agreement
        interval_days = 30
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)

        for bill, amount_per_cycle in enumerate(payment_amounts):
            product_list = []
            
            total_agreed_amount = sum(line.agreed_amount for line in self.argreement_line_ids)

            if total_agreed_amount == 0:
                raise UserError("Total agreed amount is zero. Check your agreement lines.")

            for line in self.argreement_line_ids:
                product = self.env['product.product'].search([('default_code', '=', "RENTAL")], limit=1)
                if not product:
                    raise UserError(f"Product not found for billboard ID: {line.billboard_id}")

                # Calculate the proportional amount for this line
                line_amount = round((line.agreed_amount / total_agreed_amount) * amount_per_cycle, 2)

                vals_invoice_line = {
                    'product_id': product.id,
                    'name': f"{product.name} ({line.billboard_id})",
                    'quantity': 1, #self.contract_type_id.sum_month,
                    'price_unit': line_amount,  # Use rounded line amount
                    'tax_ids': [(6, 0, [])],  
                }
                product_list.append((0, 0, vals_invoice_line))

            vals_invoice = {
                'move_type': 'out_invoice',
                'partner_id': self.partner_id.id,
                'invoice_date': fields.Date.today(),
                'invoice_origin': self.name,
                'agreement_id': self.id,
                'invoice_line_ids': product_list,
                'invoice_date_due': duedate,
                'currency_id': self.currency_id.id,
            }

            # Create the invoice
            inv_obj = self.env['account.move'].create(vals_invoice)
            inv_obj.action_post()

            # Increment due date for the next invoice
            duedate += timedelta(days=interval_days)

        return {
            'name': _('Customer Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'view_id': self.env.ref('lod_rental_space.account_move_two_action_form').id, 
            'res_id': inv_obj.id,
        }
    
    def smart_button_inv(self):
        action = self.env['ir.actions.actions']._for_xml_id('lod_rental_space.account_move_two_action')
        action['domain'] = [('agreement_id', '=', self.id)]
        return action

    def _agreement_count_customer_invoice(self):
       for rec in self: 
            lent_invoice = self.env['account.move'].search_count([('agreement_id', '=', self.id)])  
            rec.agree_count_customer_invoice = lent_invoice
# Agreements 'open' state And Create the invoice

    def contract_close(self):
        billboards = self.env['rental.space'].browse(self.billboard_id.id)
        rental_id = self.env['rental.space'].search([('order_id','=',self.quotation_rfe.id)])
        rental_id.start_date = False
        rental_id.end_date = False
        rental_id.agreement_id =False
        rental_id.user_id =False
        rental_id.partner_id =False
        rental_id.order_id =False
        rental_id.rental_count_customer_sale =False
        rental_id.remark_id =False
        # rental_id.owner_ids =False
        rental_id.days_values =False
        rental_id.state = 'available'
        self.state = 'closed'
        self._handle_state_and_reminders({'state': 'closed'})
        return True
 
    

    def contract_cancel(self):
        billboardss = self.env['rental.space'].browse(self.billboard_id.id)
        rental_id = self.env['rental.space'].search([('order_id','=',self.quotation_rfe.id)])
        rental_id.start_date = False
        rental_id.end_date = False
        rental_id.agreement_id =False
        rental_id.user_id =False
        rental_id.partner_id =False
        rental_id.order_id =False
        rental_id.remark_id =False
        rental_id.rental_count_customer_sale =False
        # rental_id.owner_ids =False
        rental_id.days_values =False
        rental_id.state = 'available'
        self.state = 'cancel'
        self._handle_state_and_reminders({'state': 'cancel'})
        return True
     

    
    def contract_draft(self):
        return self.write({'state': 'draft'})       

class RentalSpaceAgreementLine(models.Model):
    _name = "agreement.billboard.lines"
    _description = "Billboard Agreement Lines"
    
    # _order = "name"
    argreement_id = fields.Many2one('agreement.billboard', string='argreement')
    billboard_id = fields.Char( string="Billboard", readonly=True)
    location_branch_id = fields.Char( string='Location Branch', required=True)
    rental_area_sizes = fields.Char( string='Size', readonly=True)
    location_ids = fields.Char( string="Location", readonly=True)
    agreed_amount = fields.Float(string="Amount", readonly=True, store=True)
    product_id = fields.Char(string="Product Variant", readonly=True)
    # product_uom_qty = fields.Char(string="Quantity", readonly=True)
    product_uom_qty = fields.Float(string="Quantity", readonly=False )
    product_uom = fields.Char(string="UoM", readonly=True)
    price_unit = fields.Char(string="Unit Price", readonly=True)
    discount= fields.Char(string="Disc.%", readonly=True)
    currency_id = fields.Many2one('res.currency', string="Currency",related='argreement_id.currency_id')
    

class ContractType(models.Model):
    _name = 'agreement.contract.type'
    _description = "Contract Type"

    name = fields.Char(string='Contract Type', index=True)
    sum_month = fields.Integer(string='Sum Month', index=True)

class AgreementCycle(models.Model):
    _name = 'agreement.cycle'
    _description = "Agreement Cycle"

    name = fields.Char(string='Cycle', index=True)
    sum_month = fields.Integer(string='Sum Month', index=True)


