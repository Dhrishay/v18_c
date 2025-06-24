from odoo import api, fields, models


class SerialNumberWizard(models.TransientModel):
    _name = "serial.number.wizard"
    _description = 'Serial Number Wizard'

    asset_id = fields.Many2one('account.asset')
    serial_number = fields.Many2one('serial.numbers')
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,default=lambda self: self.env.company
    )

    def action_confirm(self):
        """Action when the wizard is confirmed"""
        lot_id = self.env['stock.lot'].search([
            ('name', '=', self.serial_number.name)
        ])
        if lot_id:
            self.asset_id.update({
                'location_id': lot_id.location_id.id, 
                'product_id': lot_id.product_id.id, 
                'product_tmpl_id': lot_id.product_id.product_tmpl_id.id, 
                'serial_no': lot_id.name
            })
            self.asset_id.validate()
