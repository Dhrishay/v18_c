from odoo import api, fields, models, _


class LODResCurrencyRate(models.Model):
    _inherit = 'res.currency.rate'
    _description = 'Currency Rate Extend'

    rate_sale = fields.Float(
        string='Rent Rate', digits=(12, 6),
        help="The rate used for sales transactions.",
        default=1
    )
    inver_rate_sale = fields.Float(
        string='Unit per Sale Rate', digits=(12, 6),
        help="The unit per sale rate.",
        compute="_compute_inver_rate_sale" ,default=1
    )

    @api.depends('rate_sale')
    def _compute_inver_rate_sale(self):
        for rec in self:
            rec.inver_rate_sale = 1 / rec.rate_sale if rec.rate_sale else 1


class LODResCurrency(models.Model):
    _inherit = 'res.currency'
    _description = 'Currency Extend'

    inverse_sale_rate = fields.Float(
        string='Inverse Sale Rate', digits=(12, 6),
        help="The inverse of the current sale rate.",
        compute="_compute_current_sale_rate", store=True
    )
    rate_sale = fields.Float(
        string='Rent Rate', digits=(12, 6),
        help="The current sale rate.",
        compute="_compute_current_sale_rate", store=True
    )
    sale_rate = fields.Float ( string="Sale Rate")
    buy_rate = fields.Float ( string="Buy Rate")

    @api.depends('rate_ids.rate_sale', 'rate_ids.name')
    @api.depends_context('to_currency', 'date', 'company', 'company_id')
    def _compute_current_sale_rate(self):
        date = self._context.get('date') or fields.Date.context_today(self)
        company = self.env['res.company'].browse(
            self._context.get('company_id')
        ) or self.env.company

        CurrencyRate = self.env['res.currency.rate'].sudo()

        for currency in self: 
            rate = CurrencyRate.search([
                ('currency_id', '=', currency.id), 
                ('name', '<=', date),
                '|',('company_id', '=', company.id),
                ('company_id', 'parent_of', company.id),
            ], order='name desc ', limit=1)

            if rate:
                currency.rate_sale = rate.rate_sale or 1
                currency.inverse_sale_rate = rate.inver_rate_sale or 1
            else:
                currency.rate_sale = 1
                currency.inverse_sale_rate = 1

    @api.model
    def _get_converse_rate(self, from_currency, to_currency, company=None, date=None, move_type=None):
        if from_currency == to_currency:
            return 1

        company = company or self.env.company
        date = date or fields.Date.context_today(self)

        if move_type in ('out_invoice','out_refund','out_receipt'):
            inverse_rate = from_currency.with_company(company).with_context(
                to_currency=to_currency.id, date=str(date)
            ).rate_sale
        else:
            inverse_rate = from_currency.with_company(company).with_context(
                to_currency=to_currency.id, date=str(date)
            ).inverse_rate
        return inverse_rate

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('list', 'form'):
            currency_name = (self.env['res.company'].browse(
                self._context.get('company_id')
            ) or self.env.company).currency_id.name
            fields_maps = [
                [['company_rate', 'rate'], _('Unit per %s', currency_name)],
                [['inverse_company_rate', 'inverse_rate'], _('%s Buy Rate', currency_name)],
            ]
            for fnames, label in fields_maps:
                xpath_expression = '//list//field[' + " or ".join(f"@name='{f}'" for f in fnames) + "][1]"
                node = arch.xpath(xpath_expression)
                if node:
                    node[0].set('string', label)
        return arch, view
