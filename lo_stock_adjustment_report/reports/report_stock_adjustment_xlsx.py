from odoo import models
import io
from datetime import datetime
import xlsxwriter


class ProductSalesReports(models.AbstractModel):
    _name = 'report.lo_stock_adjustment_report.adj_rpt_tpl'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Stock Adjustment report'

    def generate_xlsx_report(self, workbook, data, records):
        sheet = workbook.add_worksheet('Never Sold')
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D3D3D3',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        text_format = workbook.add_format({
            'border': 1,
            'valign': 'top',
            'text_wrap': True
        })
        seq_format = workbook.add_format({
            'border': 1,
            'align': 'top',
            'text_wrap': True,
            'valign': 'vcenter'
        })

        number_format = workbook.add_format({
            'border': 1,
            'valign': 'top',
            'align': 'right',
            'num_format': '#,##0.00'
        })

        company_name = data.get('company_name', '')
        company_address = data.get('company_address', '')
        start_date = data.get('start_date', '')
        end_date = data.get('end_date', '')

        sheet.set_column('A:A', 5)  # Column A (No.)
        sheet.set_column('B:G', 15)  # Column B (Store Code)
        sheet.set_column('H:H', 40)  # Columns C-D (Div Name and Dept Name)
        sheet.set_column('I:I', 20)  # Column G (Barcode)
        sheet.set_column('J:M', 15)  # Column H (Description)

        sheet.merge_range('A1:M1', f"Store: {company_name} (Address: {company_address})", header_format)
        sheet.merge_range('A2:M2', f"Date: {start_date} to {end_date}", header_format)

        headers = [
            'No.', 'Store Code', 'Div Name', 'Dept Name', 'Sub-Dept Name',
            'Product ID', 'Barcode', 'Description', 'Reason Adjustment',
            'ADJ-Qty', 'Cost of unit', 'Cost Amount', 'Price Amount'
        ]
        for col, header in enumerate(headers):
            sheet.write(4, col, header, header_format)

        row = 5
        no = 1
        for idx, rec in enumerate(records):
            for line in rec.order_line_ids:
                if line:
                    sheet.write(row, 0, no, seq_format)
                    sheet.write(row, 1, rec.company_id.pc_code or '', text_format)
                    sheet.write(row, 2, line.product_template_id.categ_id.division_name or '', text_format)
                    sheet.write(row, 3, line.product_template_id.categ_id.department_name or '', text_format)
                    sheet.write(row, 4, line.product_template_id.categ_id.sub_department_name or '', text_format)
                    sheet.write(row, 5, str(line.product_template_id.default_code) or '', text_format)
                    sheet.write(row, 6, str(line.product_barcode) or '', text_format)
                    sheet.write(row, 7, line.product_template_id.display_name or '', text_format)
                    sheet.write(row, 8, rec.description or '', text_format)
                    sheet.write(row, 9, line.diff_qty or 0, number_format)
                    sheet.write(row, 10, line.product_template_id.standard_price or 0, number_format)
                    sheet.write(row, 11, line.diff_qty * line.product_template_id.standard_price or 0, number_format)
                    sheet.write(row, 12, line.diff_qty * line.product_template_id.list_price or 0, number_format)
                    row += 1
                    no += 1
        sheet.freeze_panes(5, 0)


class StockAdjustmentReport(models.AbstractModel):
    _name = 'report.lo_stock_adjustment_report.stock_adjustment_report'
    _description = 'Stock Adjustment Report'

    def _get_report_values(self, docids, data=None):
        docids = data.get('result_ids', [])
        docs = self.env['multi.scrap'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'multi.scrap',
            'docs': docs,
            'data': data,
        }
