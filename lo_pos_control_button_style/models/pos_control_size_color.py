# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

COLORS = [
    "No color",
    "Red",
    "#FFA400",
    "Yellow",
    "Cyan",
    "Purple",
    "#efdecd",
    "Teal",
    "Blue",
    "#e30b5d",
    "Green",
    "Violet",
]

class ControlSizeWidth(models.Model):
    _name = 'pos.control.size.color'
    _description = 'POS Control Button Size and Color'

    name = fields.Char(string="Name", required=True)
    config_ids = fields.Many2many(
        'pos.config', required=True, string="Configurations"
    )
    line_ids = fields.One2many(
        'pos.control.size.color.line', 'parent_id',
        string="Control Button Lines"
    )
    height = fields.Integer(string="Button Height")
    width = fields.Integer(string="Button Width")

    @api.model
    def default_get(self, fields):
        "Default set value of height and width"
        result = super().default_get(fields)
        defaults = {'height': 125, 'width': 270}
        result.update({
            key: value for key, value in defaults.items() if key in fields
        })
        return result

    @api.constrains('height')
    def _check_height(self):
        """
        Ensure the height is within the valid range of 100px to 200px.
        """
        for record in self:
            if record.height < 100 or record.height > 200:
                raise ValidationError(_("Height must be between 100 and 200."))

    @api.constrains('width')
    def _check_width(self):
        """
        Ensure the width is within the valid range of 200px to 300px.
        """
        for record in self:
            if record.width < 200 or record.width > 300:
                raise ValidationError(_("Width must be between 200 and 300."))


    @api.model
    def get_color_size(self, config_id):
        """
        Fetches the button size and color details for a given configuration.
        """
        rec = self.search([('config_ids', 'in', [config_id])])
        if rec:
            final_dict = {}
            if rec.height:
                final_dict['button_height'] = rec.height
            if rec.width:
                final_dict['button_width'] = rec.width
            if rec.line_ids:
                final_dict['color_lines'] = [
                            {
                                'color': COLORS[line.button_color],
                                'name': line.button_id.name,
                            }
                            for line in rec.line_ids
                        ]
            return final_dict


    @api.constrains('config_ids')
    def _check_config_ids(self):
        """
        Ensures no duplicate configurations are assigned.
        """
        for rec in self:
            config = self.search([('config_ids', 'in', rec.config_ids.ids)])
            if config and len(config) > 1:
                config_list = [i.name for i in config.config_ids if i.id in rec.config_ids.ids]
                config_str = ','.join(config_list)
                raise ValidationError(_(f'A configuration already exists for the {config_str}.'))


class ControlSizeWidthLine(models.Model):
    _name = 'pos.control.size.color.line'
    _description = 'POS Control Button Size and Color Lines'

    button_id = fields.Many2one(
        'pos.action.button',string="Button Name", required=True
    )
    button_color = fields.Integer(
        string="Button Color", required=True
    )
    parent_id = fields.Many2one(
        'pos.control.size.color', string="Parent"
    )
