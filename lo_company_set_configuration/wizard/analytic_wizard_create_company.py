from odoo import api, models, registry, fields, _
from odoo.exceptions import ValidationError
from random import randint


class AnalyticWizardCreateCompany(models.TransientModel):
    _name = 'analytic.create.company.wizard'
    _description = 'Analytic Account Confirmation Wizard'

    chart_template = fields.Selection(
        selection=lambda self: self.env.company._chart_template_selection()
    )
    is_create_coa = fields.Boolean(string="Create Chart Of Account?")
    country_id = fields.Many2one('res.country',string='Country')
    account_reconcile = fields.Boolean(string="Reconciliation")
    state = fields.Selection([
        ('account', 'Chart Of Account'),
        ('warehouse', 'Warehouse'),
        ('analytic_plan', 'Analytic Plan'),
        ('analytic_sub_plan', 'Analytic Sub Plan'),
        ('analytic_account', 'Analytic Account'),
        ('done', 'Done')

    ], default='account')
    warehouse_name = fields.Char()
    warehouse_code = fields.Char(
        string="Warehouse Code", size=5
    )
    is_create_analytic_plan = fields.Boolean(
        string="Create Analytic Plan?"
    )
    is_create_analytic_sub_plan = fields.Boolean(
        string="Create Analytic Sub Plan?"
    )
    is_create_analytic_account = fields.Boolean(
        string="Create Analytic Account?"
    )
    is_create_sub_sub_plan = fields.Boolean(
        string="Level 2 Plan"
    )
    analytic_plan_ids = fields.One2many(
        'company.create.analytic.plan', 'create_company_wizard_id'
    )
    analytic_sub_plan_ids = fields.One2many(
        'company.create.analytic.plan', 'create_sub_company_wizard_id'
    )
    analytic_sub_sub_plan_ids = fields.One2many(
        'company.create.analytic.plan', 'create_sub_sub_company_wizard_id'
    )
    analytic_account_ids = fields.One2many(
        'analytic.plan.company.line', 'create_company_wizard_id',
        string="Analytic Accounts"
    )

    def action_create_level2_plan(self):
        self.is_create_sub_sub_plan = True
        return {
            'type': 'ir.actions.act_window',
            'name': _('Setup Configuration'),
            'res_model': 'analytic.create.company.wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': {
                'active_company_id': self._context.get('active_company_id')
            },
        }

    @api.model
    def default_get(self, fields):
        records = self.env['company.create.analytic.plan'].search([])
        records.unlink()
        return super(AnalyticWizardCreateCompany, self).default_get(fields)


    def action_previous_rec(self):
        state = ''
        if self.state == 'warehouse':
            state = 'account'
        elif self.state == 'analytic_plan':
            state = 'warehouse'
        elif self.state == 'analytic_sub_plan':
            state = 'analytic_plan'
        elif self.state == 'analytic_account':
            state = 'analytic_sub_plan'
        elif self.state == 'done':
            state = 'analytic_account'
        self.state = state
        return {
            'type': 'ir.actions.act_window',
            'name': _('Setup Configuration'),
            'res_model': 'analytic.create.company.wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': {
                'active_company_id': self._context.get('active_company_id')
            },
        }

    def action_confirm(self):
        if self.state == 'done':
            company = self.env['res.company'].browse(
                self._context.get('active_company_id')
            )
            company.country_id = self.country_id.id
            currency = self.country_id.currency_id.id
            if self.analytic_plan_ids:
                plan_list = []
                for plan in self.analytic_plan_ids:
                    plan_dict = {
                        'name': plan.name,
                        'color': plan.color,
                        'default_applicability': plan.default_applicability,
                    }
                    accounts = self.env['analytic.plan.company.line'].search([
                        ('plan_id', '=', plan.id)
                    ])
                    if accounts:
                        plan_dict['account_ids'] = []
                        for account in accounts:
                            plan_dict['account_ids'].append((0, 0, {
                                'name': account.name,
                                'company_id': self._context.get('active_company_id')
                            }))
                    sub_plans = self.env['company.create.analytic.plan'].search([
                        ('parent_id', '=', plan.id)
                    ])
                    if sub_plans:
                        plan_dict['children_ids'] = []
                        for sub_plan in sub_plans:
                            sub_plan_dict = {
                                'name': sub_plan.name,
                                'color': sub_plan.color,
                                'default_applicability': sub_plan.default_applicability,
                                'company_id': self._context.get("active_company_id"),
                                'children_ids': []
                            }
                            sub_accounts = self.env['analytic.plan.company.line'].search(
                                [('plan_id', '=', sub_plan.id)])
                            if sub_accounts:
                                sub_plan_dict['account_ids'] = []
                                for account in sub_accounts:
                                    sub_plan_dict['account_ids'].append((0, 0, {
                                        'name': account.name,
                                        'company_id': self._context.get('active_company_id')

                                    }))
                            sub_sub_plans = self.env['company.create.analytic.plan'].search([
                                ('parent_id', '=', sub_plan.id)
                            ])
                            if sub_sub_plans:
                                for level_plan in sub_sub_plans:
                                    sub_sub_plan_dict = {
                                        'name': level_plan.name,
                                        'color': level_plan.color,
                                        'default_applicability': level_plan.default_applicability,
                                        'company_id': self._context.get("active_company_id"),
                                    }
                                    sub_sub_accounts = self.env['analytic.plan.company.line'].search(
                                        [('plan_id', '=', level_plan.id)])
                                    if sub_sub_accounts:
                                        sub_sub_plan_dict['account_ids'] = []
                                        for account in sub_sub_accounts:
                                            sub_sub_plan_dict['account_ids'].append((0, 0, {
                                                'name': account.name
                                            }))
                                    sub_plan_dict['children_ids'].append((0, 0, sub_sub_plan_dict))
                            plan_dict['children_ids'].append((0, 0, sub_plan_dict))
                    plan_list.append(plan_dict)

                for plan_rec in plan_list:
                    plan = self.env['account.analytic.plan'].with_company(self._context.get('active_company_id')).create({
                        'name': plan_rec['name'],
                        'color': plan_rec['color'],
                        'default_applicability': plan_rec['default_applicability'],
                        'company_id': self._context.get("active_company_id"),
                    })
                    if plan_rec.get('children_ids'):
                        plan.with_company(self._context.get('active_company_id')).write({
                            'children_ids': plan_rec['children_ids']
                        })
                    if plan_rec.get('account_ids'):
                        plan.with_company(self._context.get('active_company_id')).write({
                            'account_ids': plan_rec['account_ids']
                        })

                    analytic_distribution_model = self.env['account.analytic.distribution.model']

                    # Create a new analytic distribution
                    if plan.account_ids:
                        account_analytic = False
                        if len(plan.account_ids) == 1:
                            account_analytic = plan.account_ids
                        else:
                            account_analytic = plan.account_ids[0]

                        company = self.env['res.company'].browse(self._context.get('active_company_id'))
                        analytic_distribution_model.sudo().create({
                            'company_id': company.id,
                            'analytic_distribution': {account_analytic.id: 100}
                        })

            if self.is_create_coa:
                template_code = self.chart_template
                company = self.env['res.company'].browse(self._context.get('active_company_id'))
                def try_loading(company=company):
                    self.env['account.chart.template']._load(
                        template_code,
                        company,
                        install_demo=False,
                    )
                self.env.cr.precommit.add(try_loading)
            self.env['stock.warehouse'].with_company(self._context.get('active_company_id')).create({
                'name': self.warehouse_name + ' - ' + 'DCTP',
                'code': self.warehouse_code,
            })
            if company:
                company.intercompany_generate_bills_refund = True
                company.intercompany_generate_sales_orders = True
                company.intercompany_generate_purchase_orders = True
                company.intercompany_purchase_journal_id = self.env['account.journal'].sudo().search(
                    [('type', '=', 'purchase'), ('company_id', '=', company.id)], limit=1).id
            company.is_set_up_done = True
            self.env.cr.commit()
            company.currency_id = currency
        return True


    def action_create_analytic_account(self):
        state = ''
        if self.state == 'account':
            state = 'warehouse'
        elif self.state == 'warehouse':
            state = 'analytic_plan'
        elif self.state == 'analytic_plan':
            state = 'analytic_sub_plan'
        elif self.state == 'analytic_sub_plan':
            state = 'analytic_account'
        elif self.state == 'analytic_account':
            state = 'done'
        self.state = state
        return {
            'type': 'ir.actions.act_window',
            'name': _('Setup Configuration'),
            'res_model': 'analytic.create.company.wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': {'active_company_id': self._context.get('active_company_id')},
        }


class AnalyticWizardCompanyLine(models.TransientModel):
    _name = 'analytic.plan.company.line'
    _description = 'Analytic Account Confirmation Line'

    create_company_wizard_id = fields.Many2one(
        'analytic.create.company.wizard'
    )
    name = fields.Char(
        string="Name", required=True
    )
    plan_id = fields.Many2one(
        'company.create.analytic.plan', string="Plan",
        required=True, ondelete='cascade'
    )


class CompanyCreateAnalyticPlan(models.TransientModel):
    _name = 'company.create.analytic.plan'
    _description = 'Company Create Analytic Plan'

    create_company_wizard_id = fields.Many2one(
        'analytic.create.company.wizard'
    )
    create_sub_company_wizard_id = fields.Many2one(
        'analytic.create.company.wizard'
    )
    create_sub_sub_company_wizard_id = fields.Many2one(
        'analytic.create.company.wizard'
    )

    def _default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True)
    color = fields.Integer('Color', default=_default_color)
    default_applicability = fields.Selection(
        selection=[
            ('optional', 'Optional'),
            ('mandatory', 'Mandatory'),
            ('unavailable', 'Unavailable'),
        ],
        string="Default Applicability",
        required=True,
        default='optional',
        readonly=False,
    )
    parent_id = fields.Many2one(
        'company.create.analytic.plan', string="Parent",
        ondelete='cascade'
    )
