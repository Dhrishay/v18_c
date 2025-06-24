from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = 'res.partner'


    request_company = fields.Boolean()
    lead_time = fields.Integer()

    def set_request_company(self):
        for rec in self.env['res.company'].sudo().search([]).mapped('partner_id'):
            if not rec.request_company:
                rec.update({'request_company': True})
