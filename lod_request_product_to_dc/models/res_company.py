from odoo import api,fields,models


class ResComapny(models.Model):
    _inherit = 'res.company'

    sequence_ro_id = fields.Many2one(
        'ir.sequence', string='Sequence RO-PO'
    )
    sequence_rfdc_id = fields.Many2one(
        'ir.sequence', string='Sequence TO-SO'
    )
    sequence_deliver_order_id = fields.Many2one(
        'ir.sequence', string='Sequence Delivery So'
    )
    vendor_id = fields.Many2one(
        'res.partner', string='Vendor Main'
    )
    sequence_sale_id = fields.Many2one(
        'ir.sequence', string="Sequence For Sale"
    )
    sequence_picking_label_id = fields.Many2one(
        'ir.sequence', string="Sequence Picking Label"
    )
    company_type = fields.Selection([
        ('franchise', 'Franchise'),
        ('master_franchise', 'Master Franchise'),
        ('dc', 'Distribution Center')
    ], string="Franchise Type")