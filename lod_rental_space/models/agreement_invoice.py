from odoo import models, fields, api, _
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    billboard_id = fields.Many2one('rental.space', string='Billboard', readonly=True)
    agreement_id = fields.Many2one('agreement.billboard', string='Agreement', readonly=True)
    # date_due = fields.Date(string='Due Date', compute="_get_default_date_due",
    #                        readonly=True, state={'draft': [('readonly', False)]}, index=True, copy=False)

    

    def create_reminder_activity(self):
        """Create a reminder activity 15 days before the due date"""
        today = fields.Date.context_today(self)
        invoices = self.search([('invoice_date_due', '=', today + timedelta(days=15)),
                                 ('state', 'not in', ['paid', 'cancel'])])
        activity_type = self.env.ref('mail.mail_activity_data_todo')  # The "To Do" activity type starts
        for invoice in invoices:
            invoice.activity_schedule(
                activity_type_id=activity_type.id,
                summary="Reminder: Invoice Due Soon",
                user_id=invoice.user_id.id or self.env.user.id,
                note=f"Invoice {invoice.name} Will be due on {invoice.invoice_date_due}.",
                date_deadline=invoice.invoice_date_due
            )
