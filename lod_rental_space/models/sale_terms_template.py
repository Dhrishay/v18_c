from odoo import fields, models, api


class AgreementTermsTemplate(models.Model):
    _name = "agreement.terms.template"
    _description = "Agreement Terms Template"
    _rec_name = 'contract_template_id'

    active = fields.Boolean(string="Active", default=True,)
    name = fields.Char(string="Name", required=True,)

    contract_template_id = fields.Char(string="Agreement Terms Template", required=True)
    text_id = fields.Html(string="Terms Template", translate=True,)
