from odoo import api, fields, models


class AssetChangeLocationWizard(models.TransientModel):
    _name = "asset.change.location.wizard"
    _description = 'Asset Change Location Wizard'

    asset_id = fields.Many2one('account.asset')
    location_id = fields.Many2one('stock.location', 'Location', related='asset_id.location_id')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, index=True, default=lambda self: self.env.company,
        help="Company related to this journal")
    location_dest_id = fields.Many2one('stock.location', 'Destination Location')
    note = fields.Text('Notes')

    def action_confirm(self):
        """Action when the wizard is confirmed"""
        self.asset_id.update({
            'location_id': self.location_dest_id.id,
            'location_dest_id': self.location_dest_id.id,
            'note': self.note,
            'company_id': self.company_id.id,
        })
        self.asset_id.with_company(self.env.company).create_internal_tranfer()
