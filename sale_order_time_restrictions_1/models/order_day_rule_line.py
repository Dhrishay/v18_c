from odoo import models, fields, api
from odoo.exceptions import ValidationError


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

     @api.constrains('start_time', 'end_time')
     def _check_start_end_time(self):
          for line in self:
               if line.start_time and line.end_time:
                    if not (0 <= line.start_time <= 24 and 0 <= line.end_time <= 24):
                         raise ValidationError("Start and end times must be in 24-hour format between 0 and 24.")
                    if line.start_time >= line.end_time:
                         raise ValidationError("Start time must be less than end time.")
