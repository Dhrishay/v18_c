from odoo import models, fields, api

class ReportRentalSpaceWizard(models.TransientModel):
    _name = 'report.rental.space.wizard'
    _description = 'Report Rental Space Wizard'

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    state = fields.Selection([
        ('all', 'All'),
        ('available', 'Available'),
        ('booking', 'Booking'),
        ('occupied', 'Occupied'),
        ('done', 'Done')
    ], string='State', default='all')

    def print_report(self):
        # Filter rental spaces based on date range and state
        rental_spaces = self.env['rental.space'].search([
            ('date_end', '>=', self.start_date),
            ('start_date', '<=', self.end_date),
            ('state', '=', self.state) if self.state != 'all' else (),
        ])

        # Calculate state counts and other metrics
        state_counts = {}
        for space in rental_spaces:
            state_counts[space.state] = state_counts.get(space.state, 0) + 1

        # Prepare report data
        report_data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'state_counts': state_counts,
            # Add other metrics and data as needed
        }

        # Return the report action
        return self.env.ref('lod_rental_space.report_rental_space_template').report_action(self, data=report_data)