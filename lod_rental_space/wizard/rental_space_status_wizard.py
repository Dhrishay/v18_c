from odoo import models, fields

class RentalSpaceStatusWizard(models.TransientModel):
    _name = 'rental.space.status.wizard'
    _description = 'Rental Space Status Wizard'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    state = fields.Selection([
        ('all', 'All'),
        ('available', 'Available'),
        ('booking', 'Booking'),
        ('occupied', 'Occupied'),
        ('done', 'Done')
    ], string='State', required=True, default='all')
    rental_space_ids = fields.Many2many('rental.space', string='Rental Spaces', readonly=True)

    def generate_report(self):
        # Filter rental spaces by date range and state
        domain = [('start_date', '<=', self.end_date), ('end_date', '>=', self.start_date)]
        if self.state != 'all':
            domain.append(('state', '=', self.state))

        rental_spaces = self.env['rental.space'].search(domain)

        # Prepare rental space data for the report
        self.rental_space_ids = rental_spaces

        state_counts = {state: 0 for state in ['available', 'booking', 'occupied', 'done']}
        for space in rental_spaces:
            state_counts[space.state] += 1

        report_data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'state_counts': state_counts,
        }

        # Trigger the report action
        return self.env.ref('lod_rental_space.rental_space_status_report_action').report_action(self, data=report_data)
