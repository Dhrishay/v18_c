from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    request_type = fields.Boolean(string='Request Type',default=False)
