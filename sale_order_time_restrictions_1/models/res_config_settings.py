from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
     _inherit = 'res.config.settings'

     order_start_time = fields.Float(string='Start Time', related='company_id.order_start_time', readonly=False)
     order_end_time = fields.Float(string='End Time', related='company_id.order_end_time', readonly=False)
     rule_id = fields.Many2one('order.day.rule', string='Restricted Days Rule', related='company_id.rule_id', readonly=False, help="Select the rule defining allowed days and product categories.")





