from odoo import api, fields, models
import random
import string


class AssetSerialNumbers(models.TransientModel):
    _name = "asset.serial.number"
    _description = "Asset Serial Number"

    serial_number = fields.Char()
    asset_id = fields.Many2one('account.asset')
    location_id = fields.Many2one('stock.location', 'Location')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, index=True, default=lambda self: self.env.company)
    check_lot = fields.Boolean('Check Lot')
    product_id = fields.Many2one('product.product', string='Product')
    lot_id = fields.Many2one('stock.lot', 'Lot')
    serial_numbers = fields.Many2one('serial.numbers')

    def action_confirm(self):
        chars = string.ascii_uppercase + string.digits
        asset_id = self.asset_id
        if not self.product_id:
            product_id = self.env['product.product'].sudo().create({
                'name' : 'Asset' +' '+ self.asset_id.name,
                'is_storable' : True,
                'tracking':'serial',
                'standard_price': asset_id.original_value,
                'invoice_policy': 'order',
                'default_code': 'ASSET-' + ''.join(random.choices(chars, k=8)),
                'property_account_expense_id': asset_id.account_asset_id.id,
            })
            stock_quant = self.env['stock.quant'].with_context({'inventory_mode': True}).sudo().create({
                'location_id': self.location_id.id,
                'product_id': product_id.id,
                'inventory_quantity': 1.0,
                'inventory_quantity_auto_apply': 1.0
            }).action_apply_inventory()
            lot_final = self.env['stock.lot'].create({
                'name': self.serial_number,
                'product_id': product_id.id,
                'location_id': self.location_id.id,
            })
            asset_id.update({
                'serial_no': lot_final.name,
                'product_id': lot_final.product_id.id,
                'location_id': self.location_id.id,
            })
        elif self.lot_id:
            asset_id.update({
                'serial_no': self.lot_id.name,
                'product_id': self.lot_id.product_id.id,
                'location_id': self.lot_id.location_id.id,
            })
        asset_id.validate()
