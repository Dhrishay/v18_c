from odoo import api, models, registry, fields, _


class AnalyticPlan(models.Model):
    _inherit = 'account.analytic.plan'

    company_id = fields.Many2one('res.company', string="Company")



