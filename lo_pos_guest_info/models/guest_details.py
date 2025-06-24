# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by laoodoo.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class GuestDetail(models.Model):
    _name = 'guest.detail'
    _description = 'Guest Detail'

    age = fields.Integer('Age')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')], string="Gender"
    )
    order_id = fields.Many2one('pos.order', string='Order')
    config_id = fields.Many2one('pos.config', string='Point of Sale')
    company_id = fields.Many2one('res.company', string='Company')
    session_id = fields.Many2one('pos.session', string='Session')
    user_id = fields.Many2one('res.users', string='Cashier',)
    country_id = fields.Many2one('res.country')
    guest_age_range = fields.Selection([
        ('below_20', 'Below 20'), ('20_25', '20-25'),
        ('26_30', '26-30'), ('31_35', '31-35'),
        ('36_40', '36-40'), ('41_45', '41-45'),
        ('46_50', '46-50'), ('above_50', 'Above 50')],
        string="Guest Age", compute="_compute_guest_age_range",
        store=True, readonly=False
    )

    @api.depends('age')
    def _compute_guest_age_range(self):
        for record in self:
            if record.age < 20:
                record.guest_age_range = 'below_20'
            elif record.age >=20 and record.age <= 25:
                record.guest_age_range = '20_25'
            elif record.age >=26 and record.age <= 30:
                record.guest_age_range = '26_30'
            elif record.age >=31 and record.age <= 35:
                record.guest_age_range = '31_35'
            elif record.age >=36 and record.age <= 40:
                record.guest_age_range = '36_40'
            elif record.age >=41 and record.age <= 45:
                record.guest_age_range = '41_45'
            elif record.age >=46 and record.age <= 50:
                record.guest_age_range = '46_50'
            else:
                record.guest_age_range = '46_50'

    @api.model
    def _load_pos_data_domain(self):
        return []

    @api.model
    def _load_pos_data_fields(self):
        return [
            'id', 'age', 'gender',
            'order_id', 'company_id', 'config_id',
            'session_id', 'user_id', 'country_id'
        ]

    def _load_pos_data(self, data):
        domain = self._load_pos_data_domain()
        fields = self._load_pos_data_fields()
        return {
            'data': self.search_read(domain, fields, load=False),
            'fields': self._load_pos_data_fields(),
        }
