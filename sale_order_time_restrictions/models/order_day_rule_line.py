from odoo import models, fields


class OrderDayRuleLine(models.Model):
     _name = 'order.day.rule.line'
     _description = 'Allowed Day and time for Categories'

     rule_id = fields.Many2one('order.day.rule', required=True)
     day_of_week = fields.Selection([
          ('mon', 'monday'), ('tue', 'tuesday'), ('wed', 'wednesday'),
          ('thu', 'thursday'), ('fri', 'friday'), ('sat', 'saturday'), ('sun', 'sunday'),
     ], required=True)
     start_time = fields.Float(string='Start Time (24h)')
     end_time = fields.Float(string='End Time (24h)')

     category_ids = fields.Many2many(
          'product.category',
          'order_day_rule_line_category_rel',
          'line_id',
          'category_id',
          string='Allowed Product Categories'
     )
