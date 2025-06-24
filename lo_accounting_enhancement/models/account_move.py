# -*- coding: utf-8 -*-
from odoo import models, fields, api , _
import json
from odoo.tools.misc import formatLang
from collections import defaultdict
from odoo.exceptions import AccessError


class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_order_id = fields.Many2one(
        'sale.order', string='Sale Order'
    )
    account_id = fields.Many2one(
        'account.journal', string='Bank One',
        domain="([('type', 'in', ('cash', 'bank'))])"
    )
    account_ids = fields.Many2one(
        'account.journal', string='Bank Two',
        domain="([('type', 'in', ('cash', 'bank'))])"
    )
    tax_totals_json = fields.Char(
        string="Invoice Totals JSON", compute='_compute_tax_totals_json',
        readonly=False,
        help='Edit Tax amounts if you encounter rounding issues.'
    )
    delivery_ref = fields.Char('Delivery #')
    invoice_date = fields.Date(
        string='Invoice/Bill Date', index=True,
        copy=False, default=fields.Date.today
    )
    invoice_currency_inverse_rate = fields.Float(
        string='Currency Invert Rate',
        compute='_compute_invoice_currency_inverse_rate',
        store=True, precompute=True,
        copy=False,
        digits=0,
    )

    @api.model
    def _get_tax_totals(self, partner, tax_lines_data, amount_total, amount_untaxed, currency):

        account_tax = self.env['account.tax']

        grouped_taxes = defaultdict(
            lambda: defaultdict(
                lambda: {'base_amount': 0.0, 'tax_amount': 0.0, 'base_line_keys': set()}
            )
        )
        subtotal_priorities = {}
        for line_data in tax_lines_data:
            tax_group = line_data['tax'].tax_group_id

            # Update subtotals priorities
            if tax_group.preceding_subtotal:
                subtotal_title = tax_group.preceding_subtotal
                new_priority = tax_group.sequence
            else:
                # When needed, the default subtotal is always the most prioritary
                subtotal_title = _("Untaxed Amount")
                new_priority = 0

            if subtotal_title not in subtotal_priorities or new_priority < subtotal_priorities[subtotal_title]:
                subtotal_priorities[subtotal_title] = new_priority

            # Update tax data
            tax_group_vals = grouped_taxes[subtotal_title][tax_group]

            if 'base_amount' in line_data:
                # Base line
                if tax_group == line_data.get('tax_affecting_base', account_tax).tax_group_id:
                    # In case the base has a tax_line_id belonging to the same group as the base tax,
                    # the base for the group will be computed by the base tax's original line (the one with tax_ids and no tax_line_id)
                    continue

                if line_data['line_key'] not in tax_group_vals['base_line_keys']:
                    # If the base line hasn't been taken into account yet, at its amount to the base total.
                    tax_group_vals['base_line_keys'].add(line_data['line_key'])
                    tax_group_vals['base_amount'] += line_data['base_amount']

            else:
                # Tax line
                tax_group_vals['tax_amount'] += line_data['tax_amount']

        # Compute groups_by_subtotal
        groups_by_subtotal = {}
        for subtotal_title, groups in grouped_taxes.items():
            groups_vals = [{
                'tax_group_name': group.name,
                'tax_group_amount': amounts['tax_amount'],
                'tax_group_base_amount': amounts['base_amount'],
                'formatted_tax_group_amount': formatLang(self.env, amounts['tax_amount'], currency_obj=currency),
                'formatted_tax_group_base_amount': formatLang(self.env, amounts['base_amount'], currency_obj=currency),
                'tax_group_id': group.id,
                'group_key': '%s-%s' % (subtotal_title, group.id),
            } for group, amounts in sorted(groups.items(), key=lambda l: l[0].sequence)]

            groups_by_subtotal[subtotal_title] = groups_vals

        # Compute subtotals
        subtotals_list = []  # List, so that we preserve their order
        previous_subtotals_tax_amount = 0
        for subtotal_title in sorted((sub for sub in subtotal_priorities), key=lambda x: subtotal_priorities[x]):
            subtotal_value = amount_untaxed + previous_subtotals_tax_amount
            subtotals_list.append({
                'name': subtotal_title,
                'amount': subtotal_value,
                'formatted_amount': formatLang(self.env, subtotal_value, currency_obj=currency),
            })

            subtotal_tax_amount = sum(group_val['tax_group_amount'] for group_val in groups_by_subtotal[subtotal_title])
            previous_subtotals_tax_amount += subtotal_tax_amount

        # Assign json-formatted result to the field
        return {
            'amount_total': amount_total,
            'amount_untaxed': amount_untaxed,
            'formatted_amount_total': formatLang(self.env, amount_total, currency_obj=currency),
            'formatted_amount_untaxed': formatLang(self.env, amount_untaxed, currency_obj=currency),
            'groups_by_subtotal': groups_by_subtotal,
            'subtotals': subtotals_list,
            'allow_tax_edition': False,
        }


    @api.depends('line_ids.amount_currency', 'line_ids.tax_base_amount', 'line_ids.tax_line_id', 'partner_id','currency_id', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json(self):
        for move in self:
            if not move.is_invoice(include_receipts=True):
                # Non-invoice moves don't support that field (because of multicurrency: all lines of the invoice share the same currency)
                move.tax_totals_json = None
                continue

            tax_lines_data = move._prepare_tax_lines_data_for_totals_from_invoice()

            move.tax_totals_json = json.dumps({
                **self._get_tax_totals(move.partner_id, tax_lines_data, move.amount_total, move.amount_untaxed,
                                       move.currency_id),
                'allow_tax_edition': move.is_purchase_document(include_receipts=False) and move.state == 'draft',
            })

    def _prepare_tax_lines_data_for_totals_from_invoice(self, tax_line_id_filter=None, tax_ids_filter=None):

        self.ensure_one()

        tax_line_id_filter = tax_line_id_filter or (lambda aml, tax: True)
        tax_ids_filter = tax_ids_filter or (lambda aml, tax: True)

        balance_multiplicator = -1 if self.is_inbound() else 1
        tax_lines_data = []

        for line in self.line_ids:
            if line.tax_line_id and tax_line_id_filter(line, line.tax_line_id):
                tax_lines_data.append({
                    'line_key': 'tax_line_%s' % line.id,
                    'tax_amount': line.amount_currency * balance_multiplicator,
                    'tax': line.tax_line_id,
                })

            if line.tax_ids:
                for base_tax in line.tax_ids.flatten_taxes_hierarchy():
                    if tax_ids_filter(line, base_tax):
                        tax_lines_data.append({
                            'line_key': 'base_line_%s' % line.id,
                            'base_amount': line.amount_currency * balance_multiplicator,
                            'tax': base_tax,
                            'tax_affecting_base': line.tax_line_id,
                        })

        return tax_lines_data

    def merge_account_move(self):
        partner = []
        for rec in self:
            partner.append(rec.partner_id.id)
        line = []
        reference = []
        for record in self:
            if record.state == 'draft':
                record.state = 'cancel'
            else:
                raise AccessError(_("This Invoice/Bill is not 'Draft' status"))

            for part in partner:
                if record.partner_id.id != part:
                    raise AccessError(_('Please, Check Partner have to the same'))

            for l in record.invoice_line_ids:
                vals_line = [0,0, {
                    'product_id': l.product_id.id,
                    'name': l.product_id.display_name,
                    'quantity': l.quantity,
                    'product_uom_id': l.product_uom_id.id,
                    'price_unit': l.price_unit,
                    'tax_ids': [(6, 0, l.tax_ids.ids)],
                    # 'analytic_tag_ids': [(6, 0, l.analytic_tag_ids.ids)],
                    # 'analytic_account_id': l.analytic_account_id.id if not l.display_type and l.analytic_account_id.id else False,
                }]
                line.append(vals_line)

            vals = {
                'partner_id': record.partner_id.id,
                'partner_shipping_id': record.partner_shipping_id.id,
                'move_type': record.move_type,
                'company_id': record.company_id.id,
                'journal_id': record.journal_id.id,
                'currency_id': record.currency_id.id,
                'fiscal_position_id': (record.fiscal_position_id or record.fiscal_position_id._get_fiscal_position(record.partner_id)).id,
                'invoice_date': fields.Datetime.now(),
                'payment_reference': '',
                'invoice_line_ids': line,
            }
            reference.append(record.payment_reference)

        vals['payment_reference'] = reference
        invoice_id = self.create(vals)

        # return True

    @api.depends('currency_id', 'company_currency_id', 'company_id', 'invoice_date')
    def _compute_invoice_currency_inverse_rate(self):
        for move in self:
            if move.is_invoice(include_receipts=True):
                if move.currency_id:
                    move.invoice_currency_inverse_rate = self.env['res.currency']._get_converse_rate(
                        from_currency=move.currency_id,
                        to_currency=move.company_currency_id,
                        company=move.company_id,
                        date=move._get_invoice_currency_rate_date(),
                        move_type=move.move_type
                    )
                else:
                    move.invoice_currency_inverse_rate = 1

    @api.depends('currency_id', 'company_currency_id', 'company_id', 'invoice_date')
    def _compute_invoice_currency_rate(self):
        for move in self:
            if move.is_invoice(include_receipts=True):
                if move.currency_id:
                    move.invoice_currency_rate = self.env['res.currency']._get_converse_rate(
                        from_currency=move.company_currency_id,
                        to_currency=move.currency_id,
                        company=move.company_id,
                        date=move._get_invoice_currency_rate_date(),
                        move_type=move.move_type
                    )
                else:
                    move.invoice_currency_rate = 1
