from odoo import models, fields


class OrderDayRule(models.Model):
     _name = 'order.day.rule'
     _description = 'Order Day Rule'
     _rec_name = 'name'

     name = fields.Char(string='Name', required=True)
     line_ids = fields.One2many('order.day.rule.line', 'rule_id', string='Allowed Day Rules')