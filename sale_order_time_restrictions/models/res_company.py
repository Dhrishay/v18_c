from odoo import models, fields


class Company(models.Model):
    _inherit = 'res.company'

    order_start_time = fields.Float(string='Start Time')
    order_end_time = fields.Float(string='End Time')
    rule_id = fields.Many2one('order.day.rule', string='Restricted Days Rule', help="Select the rule defining allowed days and product categories.")