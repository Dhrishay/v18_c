from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    class_code = fields.Char(tracking=True)
    is_create_model = fields.Boolean()

    @api.depends('account_type')
    def _compute_can_create_asset(self):
        for record in self:
            record.can_create_asset = record.account_type in (
                'asset_fixed',
                'asset_non_current',
                'asset_property_equipment'
            )
            record.form_view_ref = 'account_asset.view_account_asset_form'

    def generate_asset_model(self):
        return {
            'name': _('Asset Model'),
            'res_model': 'account.asset',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'context': {'default_state': 'model','is_create_chart_account': True},
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    @api.constrains('class_code')
    def _constrains_allowed_journal_ids(self):
        avalible_code = self.search([('class_code', '=', self.class_code),('id', '!=', self.id)])
        if avalible_code:
            raise ValidationError(_('The class code is already in use. Please enter a different code'))

    def write(self, vals):
        result = super(AccountAccount, self).write(vals)
        for rec in self:
            company = self.env.company if not self.env.company.parent_id else self.env.company.parent_id
            seq = 'account.account.%s.%s' % (rec.id, company.id)
            sequence = self.env['ir.sequence'].sudo().search([('code', '=', seq)])
            if not sequence:
                self.env['ir.sequence'].sudo().create({
                    'name': company.name + '' + 'Sequence',
                    'code': seq,
                    'prefix': rec.class_code,
                    'padding': 5,
                    'company_id': False,
                })
            else:
                sequence.update({
                    'prefix': rec.class_code
                })
        return result
