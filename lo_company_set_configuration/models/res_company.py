from odoo import api, models, registry, fields, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_set_up_done = fields.Boolean(
        string="Set Up Done"
    )
    company_type = fields.Selection([
        ('franchise', 'Franchise'),
        ('master_franchise', 'Master Franchise'),
        ('dc', 'Distribution Center')
    ], string="Franchise Type")
    zone_id = fields.Many2one(
        'sale.zone.ordering', string="Zone"
    )
    res_partner_name_id = fields.Many2one(
        'res.partner', string="Register Partner Name"
    )
    owner_id = fields.Many2one(
        'res.partner', string="Owner"
    )
    district_id = fields.Many2one(
        'res.district', string="District"
    )
    latitude = fields.Char(string="Latitude")
    longitude = fields.Char(string="Longitude")
    wh_cd = fields.Char(string="Workplace Code")
    merchant_id = fields.Char(string="Merchant ID")
    pc_code = fields.Char(string="Branch Code")


    ## Redirect to create analytic account confirmation popup when creating company
    def action_create_configuration(self):
        return_dict = {
            'type': 'ir.actions.act_window',
            'name': _('Setup Configuration'),
            'res_model': 'analytic.create.sub.company.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_company_id': self.id},
        }
        if self.parent_id:
            return_dict['res_model'] = 'analytic.create.sub.company.wizard'
        else:
            return_dict['res_model'] = 'analytic.create.company.wizard'
        return return_dict
