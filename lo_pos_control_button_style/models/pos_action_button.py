# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ControlButtonName(models.Model):
    _name = 'pos.action.button'
    _description = 'POS Action Button'

    name = fields.Char(string="Name")


    @api.model
    def create_button_record(self, button_name):
        # Check if the button already exists by name
        button_name_exist = self.env['pos.action.button'].search([
            ('name', '=', button_name)], limit=1
        )

        if not button_name_exist:
            # If it doesn't exist, create a new button record
            self.env['pos.action.button'].create({
                'name': button_name,
            })





