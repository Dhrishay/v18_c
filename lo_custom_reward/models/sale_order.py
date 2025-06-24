from odoo import fields, models
from datetime import datetime

from odoo.addons.sale_loyalty.models.sale_order import SaleOrder

def _get_program_domain(self):
    """
    Returns the base domain that all programs have to comply to.
    """
    self.ensure_one()
    today = datetime.now()
    
    return [('active', '=', True), ('sale_ok', '=', True),
            *self.env['loyalty.program']._check_company_domain([self.company_id.id, self.company_id.parent_id.id]),
            '|', ('pricelist_ids', '=', False), ('pricelist_ids', 'in', [self.pricelist_id.id]),
            '|', ('date_from', '=', False), ('date_from', '<=', today),
            '|', ('date_to', '=', False), ('date_to', '>=', today)]

def _get_trigger_domain(self):
    """
    Returns the base domain that all triggers have to comply to.
    """
    self.ensure_one()
    today = datetime.now()
    return [('active', '=', True), ('program_id.sale_ok', '=', True),
            *self.env['loyalty.program']._check_company_domain([self.company_id.id, self.company_id.parent_id.id]),
            '|', ('program_id.pricelist_ids', '=', False),
                    ('program_id.pricelist_ids', 'in', [self.pricelist_id.id]),
            '|', ('program_id.date_from', '=', False), ('program_id.date_from', '<=', today),
            '|', ('program_id.date_to', '=', False), ('program_id.date_to', '>=', today)]

SaleOrder._get_program_domain = _get_program_domain
SaleOrder._get_trigger_domain = _get_trigger_domain