# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields
from odoo import api, fields, models, _

class res_partner(models.Model):
    _inherit= 'res.partner'
    
    check_credit = fields.Boolean('Check Credit')
    credit_limit_on_hold  = fields.Boolean('Credit limit on hold')
    credit_limit = fields.Float('Credit Limit')
    credit_start_date = fields.Datetime('Credit Start from')
    is_credit_group = fields.Boolean('Credit Group', compute='_check_credit_config_group')
    
    @api.depends_context('company')
    def _credit_debit_get(self):
        if not self.ids:
            self.debit = False
            self.credit = False
            return

        domain = [
            ('parent_state', '=', 'posted'),
            ('company_id', 'child_of', self.env.company.root_id.id),
            ('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']),
            ('partner_id', 'in', self.ids),('move_id.payment_state', '!=', 'paid'),
            ('reconciled', '!=', True)
        ]

        # Grouping by partner and account type (receivable/payable)
        account_move_lines = self.env['account.move.line'].search(domain
        )

        treated = self.browse()
        for line in account_move_lines:
            partner_id = line['partner_id'][0]
            partner =line['partner_id'][0]
            val = line['amount_residual']

            if line.account_id.account_type == 'asset_receivable':
                partner.credit += val
                if partner not in treated:
                    partner.debit = False
                    treated |= partner
            elif line.account_id.account_type == 'liability_payable':
                partner.debit += -val
                if partner not in treated:
                    partner.credit = False
                    treated |= partner

        remaining = (self - treated)
        remaining.debit = False
        remaining.credit = False
    
    def _check_credit_config_group(self):
        for partner in self:
            if self.env.user.has_group('dev_customer_credit_limit.credit_limit_config'):
                partner.is_credit_group = True
            else:
                partner.is_credit_group = False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
