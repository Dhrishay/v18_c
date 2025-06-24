from odoo import models, fields, api


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def get_paperformat(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            report = self.env['account.move'].browse(active_id)
            if report and report.invoice_type == 'local':
                return self.env.ref('sale_order_custom.paperformat_topflite_local_invoice')
            elif report and report.invoice_type == 'export':
                return self.env.ref('sale_order_custom.paperformat_topflite_invoice_export')

        return super().get_paperformat()
