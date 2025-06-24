from odoo import fields, models



class StockAdujstmentReportWiz(models.TransientModel):
    _name = 'stock.adjustment.report.wiz'
    _description = 'Wizard for Stock Adjustment Report'
    
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=1, default=lambda self: self.env.company)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    reason_code_id = fields.Many2one('scrap.reason.code', string="Adjustment Code", required=True)
    
    export_format = fields.Selection([
        ('pdf', 'PDF'),
        ('xlsx', 'Excel'),
    ], string="Print Out", required=True)
    
    
    def action_download_adjustment_report(self):
        query = """
        SELECT id FROM multi_scrap WHERE date BETWEEN %s AND %s
        """
        params = [self.start_date, self.end_date]

        # Filter by company_id if provided
        if self.company_id:
            query += " AND company_id = %s"
            params.append(self.company_id.id)

        # Filter by reason_code_id if provided
        if self.reason_code_id:
            query += " AND reason_code_id = %s"
            params.append(self.reason_code_id.id)

        self.env.cr.execute(query, params)
        result_ids = [row[0] for row in self.env.cr.fetchall()]
        records = self.env['multi.scrap'].browse(result_ids)
        data = {
            'company_name': self.company_id.name,
            'company_address': self.company_id.partner_id.contact_address,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else '',
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else '',
            'result_ids': result_ids,
        }
        if self.export_format == 'pdf':
            return self.env.ref('lo_stock_adjustment_report.action_stock_adjustment_report').report_action(records, data=data)
        else:
            data = {
                'company_name': self.company_id.name,
                'company_address': self.company_id.partner_id.contact_address,
                'start_date': self.start_date,
                'end_date': self.end_date,
            }
            return self.env.ref('lo_stock_adjustment_report.action_report_action_stock_sumary').report_action(records,data=data)

    