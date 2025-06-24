from PIL.EpsImagePlugin import field
from odoo import api, models, registry, fields, _
from odoo.exceptions import ValidationError
from random import randint


class AnalyticWizardCreateSubCompany(models.TransientModel):
    _name = 'analytic.create.sub.company.wizard'
    _description = "Sub Company Wizard"

    state = fields.Selection([
        ('warehouse', 'Warehouse'),
        ('analytic_account', 'Analytic Account'),
        ('analytic_budget', 'Analytic Budget'),
        ('pos_session', 'POS Session'),
        ('done', 'Done')
    ], default='warehouse')
    is_create_analytic_account = fields.Boolean(string="Create Analytic Account?")
    is_create_analytic_budget = fields.Boolean(string="Create Analytic Budget?")
    budget_name = fields.Char(string="Budget Name")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    warehouse_name = fields.Char()
    warehouse_code = fields.Char(string="Warehouse Code", size=5)
    account_name = fields.Char(string="Name")
    analytic_plan_id = fields.Many2one('account.analytic.plan', string="Plan")
    is_create_pos_session = fields.Boolean(string="Create POS Config?")
    session_name = fields.Char(string="Config Name")
    company_parent_id = fields.Many2one('res.company', string="Parent Company")
    module_pos_restaurant = fields.Boolean(string="Is a Bar/Restaurant")

    @api.model
    def default_get(self, fields):
        res = super(AnalyticWizardCreateSubCompany, self).default_get(fields)
        if self._context.get('active_company_id'):
            company = self.env['res.company'].browse(self._context.get('active_company_id'))
            if company:
                res['company_parent_id'] = company.parent_id.id
        return res

    def action_previous_rec(self):
        state = ''
        if self.state == 'analytic_account':
            state = 'warehouse'
        elif self.state == 'analytic_budget':
            state = 'analytic_account'
        elif self.state == 'pos_session':
            state = 'analytic_budget'
        elif self.state == 'done':
            state = 'pos_session'
        self.state = state
        return {
            'type': 'ir.actions.act_window',
            'name': _('Setup Configuration'),
            'res_model': 'analytic.create.sub.company.wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': {'active_company_id': self._context.get('active_company_id')},
        }

    def action_create_analytic_account(self):
        state = ''
        if self.state == 'warehouse':
            state = 'analytic_account'
        elif self.state == 'analytic_account':
            state = 'analytic_budget'
        elif self.state == 'analytic_budget':
            state = 'pos_session'
        elif self.state == 'pos_session':
            state = 'done'
        self.state = state
        return {
            'type': 'ir.actions.act_window',
            'name': _('Setup Configuration'),
            'res_model': 'analytic.create.sub.company.wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': {'active_company_id': self._context.get('active_company_id')},
        }

    def action_confirm(self):
        if self.state == 'done':
            analytic_account = False
            self.env['stock.warehouse'].with_company(self._context.get('active_company_id')).create({
                'name': self.warehouse_name,
                'code': self.warehouse_code,
            })
            company = self.env['res.company'].browse(self._context.get('active_company_id'))
            if company:
                company.intercompany_generate_bills_refund = True
                company.intercompany_generate_sales_orders = True
                company.intercompany_purchase_journal_id = self.env['account.journal'].sudo().search(
                    [('type', '=', 'purchase'), ('company_id', '=', company.parent_id.id)], limit=1).id
                company.intercompany_generate_purchase_orders = True
            if self.is_create_analytic_account:
                analytic_account = self.env['account.analytic.account'].with_company(self._context.get('active_company_id')).create({
                    'name': self.account_name,
                    'plan_id': self.analytic_plan_id.id,
                })
            if self.is_create_analytic_budget:
                self.env['budget.analytic'].with_company(self._context.get('active_company_id')).create({
                    'name': self.budget_name,
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                })
            if self.is_create_pos_session:
                company = self.env['res.company'].browse(self._context.get('active_company_id'))
                cash_account_id = self.env['account.account'].with_company(self._context.get('active_company_id')).search([('name', '=', 'Cash')], limit=1)
                journal_id = self.env['account.journal'].with_company(self._context.get('active_company_id')).create({
                    'name': 'Cash',
                    'type': 'cash',
                    'default_account_id': cash_account_id.id
                })
                self.env.cr.commit()
                account_ids = self.env['account.account'].search([('account_type', '=', 'asset_cash')], limit=1)
                self.env['pos.payment.method'].with_company(self._context.get('active_company_id')).create({
                    'name': 'Bank',
                    'journal_id': self.env['account.journal'].with_company(company.parent_id.id).search(
                        [('company_id', '=', company.parent_id.id), ('type', '=', 'bank')], limit=1).id,
                    'outstanding_account_id': account_ids.id if account_ids else False
                })
                self.env['pos.payment.method'].with_company(self._context.get('active_company_id')).create({
                    'name': 'Cash',
                    'journal_id': journal_id.id,
                })
                self.env['pos.payment.method'].with_company(self._context.get('active_company_id')).create({
                    'name': 'Customer Account',
                    'split_transactions': True
                })

                config = self.env['pos.config'].with_company(self._context.get('active_company_id')).create({
                    'name': self.session_name,
                    'module_pos_restaurant': self.module_pos_restaurant
                })
                if analytic_account:
                    config.pos_sh_analytic_account = analytic_account.id

            if analytic_account:
                analytic_distribution_model = self.env['account.analytic.distribution.model']
                company = self.env['res.company'].browse(self._context.get('active_company_id'))
                analytic_distribution_model.sudo().create({
                    'company_id': company.id,
                    'analytic_distribution': {analytic_account.id: 100}
                })
            company.is_set_up_done = True
            return True
