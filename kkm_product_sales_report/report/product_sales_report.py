from odoo import models

class ProductSalesReports(models.AbstractModel):
    _name = 'report.kkm_product_sales_report.report_template_sale_sumary'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'sale summary report'


    def generate_xlsx_report(self, workbook, data, line):
        format_STOT_left = workbook.add_format({'font_size': 12, 'align': 'left'})
        format_TNR_right_vcenter = workbook.add_format({'font_size': 12, 'align': 'left', 'valign': 'vcenter'})
        format_time_new_center_border = workbook.add_format(
            {'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter'})
        currency_format = workbook.add_format({'num_format': '#,##0.00 [$₭-lo-LA]', 'font_size': 12})

        sheet = workbook.add_worksheet('Sales Commission Report')

        # Approximate column width for 2 cm
        column_width = 3 * 7.5
        wide_width = 4 * 7.5
        
        row = 0
        col = 0

        # Write header row
        for header in data['data']['header']:
            sheet.write(row, col, header, format_time_new_center_border)
            col += 1

        # Identify currency columns (7, 8, 9, 10)
        currency_columns = [7 - 1, 8 - 1, 9 - 1, 10 - 1]  # Adjusted for zero-based index
        wide_columns = [1 - 1, 2 - 1, 11 - 1]

        # Apply column width only to currency columns
        for col_idx in currency_columns:
            sheet.set_column(col_idx, col_idx, column_width)

        for col_idx in wide_columns:
            sheet.set_column(col_idx, col_idx, wide_width)


        # Write data rows
        for datas in data['data']['data']:
            row += 1
            sheet.write(row, 1 - 1, datas['barcode'], format_TNR_right_vcenter)
            sheet.write(row, 2 - 1, datas['product_name'], format_STOT_left)
            sheet.write(row, 5 - 1, datas['uom'], format_TNR_right_vcenter)
            sheet.write(row, 6 - 1, datas['qty'], format_TNR_right_vcenter)
            sheet.write(row, 7 - 1, datas['cost'], currency_format)
            sheet.write(row, 8 - 1, datas['sale_price'], currency_format)
            sheet.write(row, 9 - 1, datas['actual_sale'], currency_format)
            sheet.write(row, 10 - 1, datas['total_cost'], format_TNR_right_vcenter)
            sheet.write(row, 11 - 1, datas['product_catagory'], format_TNR_right_vcenter)

        workbook.close()
