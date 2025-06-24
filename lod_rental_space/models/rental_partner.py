from odoo import models, fields

class RentalPartner(models.Model):
    _inherit = 'res.partner'

    rental_space_id = fields.Many2one('rental.space', string='Rental Space', readonly=True, ondelete='set null')
    
