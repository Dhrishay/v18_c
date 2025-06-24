from odoo import api, models, registry, fields, _

class PosConfig(models.Model):
    _inherit = 'pos.config'

    delivery_time = fields.Integer(
        string="Delivery Time", compute='set_delivery_time',
        readonly=False, store=True
    )

    @api.depends('company_id','company_id.delivery_time')
    def set_delivery_time(self):
        for rec in self:
            if rec.company_id.delivery_time:
                rec.delivery_time = rec.company_id.delivery_time

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    delivery_time = fields.Integer(
        string='Delivery Time', compute='set_delivery_time',
        inverse='inverse_delivery_time', readonly=False, store=True
    )

    @api.depends('pos_config_id','pos_config_id.delivery_time')
    def set_delivery_time(self):
        for rec in self:
            if rec.pos_config_id.delivery_time:
                rec.delivery_time = rec.pos_config_id.delivery_time

    def inverse_delivery_time(self):
        for rec in self:
            if rec.pos_config_id.delivery_time != rec.delivery_time:
                rec.pos_config_id.delivery_time = rec.delivery_time