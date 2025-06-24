from odoo import models, fields, api, _


class RentalAgreement(models.Model):
    _inherit = 'product.product'

    is_rental = fields.Boolean(string="Is Rental Fee")


class RentalAgreementTemplate(models.Model):
    _inherit = 'product.template'

    is_rental = fields.Boolean(string="Is Rental Fee")