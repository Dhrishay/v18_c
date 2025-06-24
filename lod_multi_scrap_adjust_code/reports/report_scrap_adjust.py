from odoo import models, fields, api, _
from datetime import datetime, timedelta
import datetime

class StockSummaryXlsx(models.AbstractModel):
    _name = "report.lod_multi_scrap_adjust_code.report_scrap_adjust_excel"
    _inherit = "report.report_xlsx.abstract"
    _description = "Scrap Adjust Report Excel"

    HEADER = ['No','Barcode','Description','On Hand','UOM','Quantity','Value Amount','Cost','Retail','Code Type']

    def generate_xlsx_report(self, workbook, data, objs):

        sheet = workbook.add_worksheet("Stock Summary Report Excel")

        title_center = workbook.add_format({"bold": True, "font_size": 16, "font": "Montserrat", "text_wrap": True, "border": False, "align": "center", 'valign': 'vcenter'})
        tb_header = workbook.add_format({"bold": True, "font_size": 12, "font": "Montserrat", "text_wrap": True, "border": True, "align": "center", 'valign': 'vcenter'})
        bold_left = workbook.add_format({"bold": True, "font_size": 12, "font": "Montserrat", "text_wrap": True, "border": False, "align": "left", 'valign': 'vcenter'})
        bold_center = workbook.add_format({"bold": True, "font_size": 12, "font": "Montserrat", "text_wrap": True, "border": False, "align": "center", 'valign': 'vcenter'})
        cell_normal = workbook.add_format({"bold": False, "font_size": 12, "font": "Montserrat", "text_wrap": True, "border": True, "align": "left", 'valign': 'vcenter'})
        number_format = workbook.add_format({"bold": False, "font_size": 12, "font": "Montserrat", "text_wrap": False, "border": True, "align": "right", 'num_format': '#,##0.00', 'valign': 'vcenter'})
        sum_number_format = workbook.add_format({"bold": True, "font_size": 12, "font": "Montserrat", "text_wrap": False, "border": True, "align": "right", 'num_format': '#,##0.00', 'valign': 'vcenter'})
        date_format = workbook.add_format({"bold": True, "font_size": 12, "font": "Montserrat", "text_wrap": False, "border": False, "align": "left", 'valign': 'vcenter'})
        text_align = workbook.add_format({"bold": False, "font_size": 12, "font": "Montserrat", "text_wrap": False, "border": False, "align": "right", 'valign': 'vcenter'})
        signature = workbook.add_format({"bold": True, "font_size": 13, "font": "Montserrat", "text_wrap": False, "border": False, "align": "center", 'valign': 'vcenter'})
        sheet.merge_range("A1:J1", "Stock Summary Report", title_center)
        sheet.merge_range("G2:J2", "STORE CODE: " + objs.company_id.merchant_id if objs.company_id.merchant_id else '' , bold_left)
        # sheet.merge_range("G2:J2", "STORE CODE: " + objs.branch_id.merchant_id , bold_left)
        sheet.merge_range("G3:J3", "STORE NAME: " + objs.company_id.name , bold_left)
        # sheet.merge_range("G3:J3", "STORE NAME: " + objs.branch_id.name , bold_left)
        sheet.merge_range("A5:E5", "Doc No: " + objs.name , bold_left)
        sheet.merge_range("A6:E6", "Description: " + objs.description if objs.description else '', bold_left)
        sheet.merge_range("A7:E7", "Code: " + objs.reason_code_id.name, bold_left)
        sheet.merge_range("G5:J5", "Status: " + objs.state.upper(), bold_left)
        sheet.merge_range("G6:J6", "Create By: " + objs.user_id.name, bold_left)
        sheet.merge_range("G7:J7", "Date: " + str(objs.create_date.strftime("%m/%d/%Y %H:%M:%S")), bold_left)

        col_header = 0
        for head in range(len(self.HEADER)):
            sheet.write(8, col_header, self.HEADER[col_header], tb_header)
            col_header += 1

        sheet.set_row(8, 40)
        sheet.set_column('A:A', 10)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 50)
        sheet.set_column('D:I', 20)
        sheet.set_column('J:J', 15)

        row = 6
        col = 0
        srNo = 1
        sum_onhand = sum_stock_value = sum_quantity = sum_cost = sum_sale_price = 0
        for sc_line in objs.order_line_ids:
            sheet.write(row + 3, col, srNo, cell_normal)
            sheet.write(row + 3, col+1, sc_line.product_id.barcode, cell_normal)
            sheet.write(row + 3, col+2, sc_line.product_id.name, cell_normal)
            sheet.write(row + 3, col+3, sc_line.on_hand, number_format)
            sheet.write(row + 3, col+4, sc_line.uom_id.name, number_format)
            sheet.write(row + 3, col+5, sc_line.quantity, number_format)
            sheet.write(row + 3, col+6, sc_line.stock_value, number_format)
            sheet.write(row + 3, col+7, sc_line.cost, number_format)
            sheet.write(row + 3, col+8, sc_line.product_id.lst_price, number_format)
            sheet.write(row + 3, col+9, sc_line.reason_code_id.code, cell_normal)

            row += 1
            srNo +=1

            sum_onhand += sc_line.on_hand
            sum_stock_value += sc_line.stock_value
            sum_quantity += sc_line.quantity
            sum_cost += sc_line.cost
            sum_sale_price += sc_line.product_id.lst_price
            
        sheet.write(row + 3, col, "", cell_normal)
        sheet.write(row + 3, col+1, "", cell_normal)
        sheet.write(row + 3, col+2, "Grand Total", tb_header)
        sheet.write(row + 3, col+3, sum_onhand, sum_number_format)
        sheet.write(row + 3, col+4, "", cell_normal)
        sheet.write(row + 3, col+5, sum_quantity, sum_number_format)
        sheet.write(row + 3, col+6, sum_stock_value, sum_number_format)
        sheet.write(row + 3, col+7, sum_cost, sum_number_format)
        sheet.write(row + 3, col+8, sum_sale_price, sum_number_format)
        sheet.write(row + 3, col+9, "", cell_normal)

        sheet.merge_range('A'+ str(row + 6) +':C'+ str(row + 6), "Request by", signature)
        sheet.merge_range('D'+ str(row + 6) +':F'+ str(row + 6), "Verify by LPS", signature)
        sheet.merge_range('G'+ str(row + 6) +':J'+ str(row + 6), "Approved by", signature)
