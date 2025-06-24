from odoo import models, fields, api
from datetime import date
import io
import xlsxwriter
from datetime import datetime
import base64


class StockDailyParser(models.AbstractModel):
    _name = 'report.lo_stock_daily_report.stock_end_report'
    _description = 'Sales PDF Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        print("\n\n\n_get_report_values-=-------------------------")
        docs = self.env['stock.end.of.day.report.wizard'].browse(docids)
        report_lines = docs._get_report_data()

        # if docs.report_name == 'amount_by_division':
        #     group_by_field = 'division_name'
        #     report_title = 'Sales Amount by Division'
        # if docs.report_name == 'amount_by_sub_department':
        #     group_by_field = 'sub_department_name'
        #     report_title = 'Sales Amount by Sub-Department'
        # if docs.report_name == 'qty_by_sub_department':
        #     group_by_field = 'sub_department_name'
        #     report_title = 'Sales Qty. By Sub-Department'

        return {
            'doc_ids': docids,
            'doc_model': 'stock.end.of.day.report.wizard',
            'docs': docs,
            'report_lines': report_lines,
            # 'group_by_field': group_by_field,
            # 'report_title': report_title,
        }

class StockEndOfDay(models.TransientModel):
     _name = 'stock.end.of.day.report.wizard'
     _description = 'Stock Report End of the day'

     date = fields.Date('Date', default=lambda self: date.today())
     report_type = fields.Selection([('stock_by_qty', 'Stock Inventory by Qty'),
                                       ('stock_by_cost', 'Stock Inventory by Cost'),
                                       ('stock_by_price', 'Stock Inventory by Price'),
                                       ], 'Report Type')
     company_id = fields.Many2one('res.company', string='Company')
     print_out = fields.Selection([('xls', 'XLS'), ('pdf', 'PDF')], 'Print Out', required=True)

     def action_print_report(self):
          print("\n\n\naction_print_report----------------------------")
          if self.print_out == 'xls':
               return self.generate_xls()
          if self.print_out == 'pdf':
               return self.generate_pdf()

     def _get_report_data(self):
          print("\n\n\n_get_report_data-----------------------")
          if self.report_type == 'stock_by_qty':
               print("if qty--------report data--------------")
               return self.get_stock_by_qty()
          elif self.report_type == 'stock_by_cost':
               print("if price--------report data----------------")
               return self.get_stock_by_cost()
          elif self.report_type == 'stock_by_price':
               print("if price--------report data----------------")
               return self.get_stock_by_price()
          return []

     def get_stock_by_qty(self):
          print("\n\n\nget_stock_by_qty--------------------")
          company_id = self.env.company.id
          print("company_id--------------------------", company_id)
          query = f"""
               SELECT
                   ROW_NUMBER() OVER (ORDER BY SUM(sq.quantity) DESC) AS sequence,
                   c.pc_code AS store_code,
                   pt.default_code AS product_code,
                   pt.name AS product_name,
                   pp.barcode AS barcode,
                   u.name AS uom,
                   SUM(sq.quantity) AS stock_qty,
                   sw.name AS warehouse_name,
                   sl.complete_name AS location_name,
                   pc.name AS category_name,
                   pc.division_name AS division_name,
                   pc.department_name AS department_name,
                   pc.sub_department_name AS sub_department_name
               FROM
                   stock_quant sq
               JOIN
                   stock_location sl ON sq.location_id = sl.id
               JOIN
                   stock_warehouse sw ON sl.location_id = sw.view_location_id
               JOIN
                   product_product pp ON sq.product_id = pp.id
               JOIN
                   product_template pt ON pp.product_tmpl_id = pt.id
               JOIN
                   uom_uom u ON pt.uom_id = u.id
               JOIN 
                    product_category pc ON pt.categ_id = pc.id
               JOIN
                    res_company c ON sq.company_id = c.id
               WHERE
                   sl.usage = 'internal'             
                   AND pt.type = 'consu'              
                   AND sq.company_id = {company_id}            
               GROUP BY
                   c.pc_code, pt.default_code, pt.name, pp.barcode, u.name, sw.name, sl.complete_name, 
                   pc.name, pc.division_name, pc.department_name,
                   pc.sub_department_name
               ORDER BY
                   stock_qty DESC;
          """
          print("query---------------------------------------------",query)
          a = self._cr.execute(query)
          print("A------------------------------",a)
          result = self._cr.dictfetchall()
          print("Records fetched:", result)
          aaaassss
          return result

     def get_stock_by_price(self):
          print("\n\n\nget_stock_by_price-----------------------------------------")
          company_id = self.env.company.id
          query = f"""
              SELECT
                  ROW_NUMBER() OVER (ORDER BY pt.list_price DESC) AS sequence,
                  pt.default_code AS product_code,
                  pt.name AS product_name,
                  pp.barcode AS barcode,
                  u.name AS uom,
                  SUM(sq.quantity) AS stock_qty,
                  sw.name AS warehouse_name,
                  sl.complete_name AS location_name,
                  pc.name AS product_category,
                  pt.list_price AS price_amount
              FROM
                  stock_quant sq
              JOIN
                  stock_location sl ON sq.location_id = sl.id
              JOIN
                  stock_warehouse sw ON sl.location_id = sw.view_location_id
              JOIN
                  product_product pp ON sq.product_id = pp.id
              JOIN
                  product_template pt ON pp.product_tmpl_id = pt.id
              JOIN
                  uom_uom u ON pt.uom_id = u.id
              JOIN 
                  product_category pc ON pt.categ_id = pc.id
              WHERE
                  sl.usage = 'internal'             
                  AND pt.type = 'consu'              
                  AND sq.company_id = {company_id}
              GROUP BY
                  pt.default_code, pt.name, pp.barcode, u.name, sw.name, sl.complete_name, pc.name, pt.list_price
              ORDER BY
                  pt.list_price DESC;
          """

          print("query---------------------------------------------", query)
          a = self._cr.execute(query)
          print("A------------------------------", a)
          result = self._cr.dictfetchall()
          print("Records fetched:", result)
          aaa
          return result

     def get_stock_by_cost(self):
          print("\n\n\nget_stock_by_cost-----------------------------------------")
          company_id = self.env.company.id
          query = f"""
                    SELECT
                        ROW_NUMBER() OVER (ORDER BY SUM(sq.quantity) DESC) AS sequence,
                        pt.default_code AS product_code,
                        pt.name AS product_name,
                        pp.barcode AS barcode,
                        u.name AS uom,
                        SUM(sq.quantity) AS stock_qty,
                        sw.name AS warehouse_name,
                        sl.complete_name AS location_name,
                        pc.name AS category_name,
                        pp.standard_price AS standard_price
                    FROM
                        stock_quant sq
                    JOIN
                        stock_location sl ON sq.location_id = sl.id
                    JOIN
                        stock_warehouse sw ON sl.location_id = sw.view_location_id
                    JOIN
                        product_product pp ON sq.product_id = pp.id
                    JOIN
                        product_template pt ON pp.product_tmpl_id = pt.id
                    JOIN
                        uom_uom u ON pt.uom_id = u.id
                    JOIN 
                         product_category pc ON pt.categ_id = pc.id
                    WHERE
                        sl.usage = 'internal'             
                        AND pt.type = 'consu'              
                        AND sq.company_id = {company_id}             
                    GROUP BY
                        pt.default_code, pt.name, pp.barcode, u.name, sw.name, sl.complete_name, pc.name, pp.standard_price
                    ORDER BY
                        standard_price DESC;
               """
          print("query---------------------------------------------", query)
          a = self._cr.execute(query)
          print("A------------------------------", a)
          result = self._cr.dictfetchall()
          print("Records fetched:", result)
          return result

     def generate_pdf(self):
          print("\n\n\ngenerate_pdf------------------")
          if self.report_type == 'stock_by_qty':
               print("if qty----------------------")
               return self.env.ref('lo_stock_daily_report.action_stock_end_report_by_qty').report_action(self)
          elif self.report_type == 'stock_by_cost':
               print("if cost----------------------")
               return self.env.ref('lo_stock_daily_report.action_stock_end_report_by_cost').report_action(self)
          elif self.report_type == 'stock_by_price':
               print("if price---------------------")
               return self.env.ref('lo_stock_daily_report.action_stock_end_report_by_price').report_action(self)

     # def generate_xls(self):
     #      print("\n\n\ngenerate_xls------------------------")
     #      if self.report_type == 'stock_by_qty':
     #           data_to_use = self.get_stock_by_qty()
     #      elif self.report_type == 'stock_by_cost':
     #           data_to_use = self.get_stock_by_cost()
     #      elif self.report_type == 'stock_by_price':
     #           data_to_use = self.get_stock_by_price()
     #      else:
     #           data_to_use = {}
     #
     #      output = io.BytesIO()
     #      workbook = xlsxwriter.Workbook(output, {'in_memory': True})
     #
     #      title_format = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 14})
     #      subtitle_format = workbook.add_format({'align': 'center'})
     #      header_format = workbook.add_format({
     #           'bold': True, 'align': 'center', 'valign': 'vcenter',
     #           'border': 1, 'bg_color': '#D9D9D9'
     #      })
     #      normal = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
     #
     #      company_name = self.env.company.name
     #      print("company_name---------------------------------",company_name)
     #      sheet = workbook.add_worksheet(company_name[:31])
     #      sheet.merge_range('A1:N1', f'Company : {company_name}', title_format)
     #      # sheet.merge_range('A2:N2', f'From {self.start_date} to {self.end_date}', subtitle_format)
     #
     #      headers = ['No', 'Store Code', 'Div Name', 'Dept Name', 'Sub Dept Name', 'Vendor Code', 'Vendor Name', 'Product ID', 'Barcode',
     #                 'Description(Lao)', 'Description(Eng)', 'Stock Qty', 'Trade Term']
     #      column_widths = [5, 12, 15, 15, 18, 15, 12, 15, 10, 25, 25, 10, 15]
     #      header_row = 2
     #
     #      for col, (header, width) in enumerate(zip(headers, column_widths)):
     #           sheet.write(header_row, col, header, header_format)
     #           sheet.set_column(col, col, width)
     #
     #      for row in range(header_row + 1, header_row + 6):
     #           for col in range(len(headers)):
     #                sheet.write(row, col, '', normal)
     #
     #      workbook.close()
     #      output.seek(0)
     #      xls_data = output.read()
     #
     #      filename = f'Stock_end{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
     #
     #      attachment = self.env['ir.attachment'].create({
     #           'name': filename,
     #           'type': 'binary',
     #           'datas': base64.b64encode(xls_data),
     #           'res_model': 'stock.end.of.day.report.wizard',
     #           'res_id': self.id,
     #           'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
     #      })
     #
     #      return {
     #           'type': 'ir.actions.act_url',
     #           'url': f'/web/content/{attachment.id}?download=true',
     #           'target': 'self',
     #      }

     def generate_xls(self):
          print("\n\ngenerate_xls------------------------")

          if self.report_type == 'stock_by_qty':
               data_to_use = self.get_stock_by_qty()
               headers = ['No', 'Store Code', 'Div Name', 'Dept Name', 'Sub Dept Name', 'Vendor Code', 'Vendor Name',
                          'Product ID', 'Barcode', 'Description(Lao)', 'Description(Eng)', 'Stock Qty', 'Trade Term']
          elif self.report_type == 'stock_by_price':
               data_to_use = self.get_stock_by_price()
               headers = ['No', 'Store Code', 'Div Name', 'Dept Name', 'Sub Dept Name', 'Vendor Code', 'Vendor Name',
                          'Product ID', 'Barcode', 'Description(Lao)', 'Description(Eng)', 'Stock Qty', 'Price Amount', 'Trade Term']
          elif self.report_type == 'stock_by_cost':
               data_to_use = self.get_stock_by_cost()
               headers = ['No', 'Store Code', 'Div Name', 'Dept Name', 'Sub Dept Name', 'Vendor Code', 'Vendor Name',
                          'Product ID', 'Barcode', 'Description(Lao)', 'Description(Eng)', 'Stock Qty', 'Cost Amount', 'Trade Term']
          else:
               data_to_use = []
               headers = []

          output = io.BytesIO()
          workbook = xlsxwriter.Workbook(output, {'in_memory': True})

          # Formatting
          title_format = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 14})
          header_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#D9D9D9'})
          normal = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})

          # Sheet and header
          company_name = self.env.company.name
          sheet = workbook.add_worksheet(company_name[:31])
          sheet.merge_range('A1:{}1'.format(chr(65 + len(headers) - 1)), f'Company : {company_name}', title_format)

          # Write headers
          for col, header in enumerate(headers):
               sheet.write(2, col, header, header_format)
               sheet.set_column(col, col, 15)

          # Write data
          for row_num, line in enumerate(data_to_use, start=3):
               col_num = 0
               sheet.write(row_num, col_num, row_num - 2, normal)  # No
               col_num += 1

               sheet.write(row_num, col_num, line.get('store_code', ''), normal);
               col_num += 1
               sheet.write(row_num, col_num, line.get('division_name', ''), normal);
               col_num += 1
               sheet.write(row_num, col_num, line.get('dept_name', ''), normal);
               col_num += 1
               sheet.write(row_num, col_num, line.get('sub_department_name', ''), normal);
               col_num += 1
               sheet.write(row_num, col_num, line.get('vendor_code', ''), normal);
               col_num += 1
               sheet.write(row_num, col_num, line.get('vendor_name', ''), normal);
               col_num += 1
               sheet.write(row_num, col_num, line.get('product_code', ''), normal);
               col_num += 1
               sheet.write(row_num, col_num, line.get('barcode', ''), normal);
               col_num += 1
               sheet.write(row_num, col_num, line.get('description_lao', ''), normal);
               col_num += 1
               sheet.write(row_num, col_num, line.get('description_eng', ''), normal);
               col_num += 1
               sheet.write(row_num, col_num, line.get('stock_qty', 0), normal);
               col_num += 1

               # Conditionally add cost/price
               if self.report_type == 'stock_by_price':
                    sheet.write(row_num, col_num, line.get('lst_price', 0), normal);
                    col_num += 1
               elif self.report_type == 'stock_by_cost':
                    sheet.write(row_num, col_num, line.get('cost_amount', 0), normal);
                    col_num += 1

               sheet.write(row_num, col_num, line.get('trade_term', ''), normal)

          workbook.close()
          output.seek(0)
          xls_data = output.read()

          filename = f'Stock_end_{self.report_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

          attachment = self.env['ir.attachment'].create({
               'name': filename,
               'type': 'binary',
               'datas': base64.b64encode(xls_data),
               'res_model': 'stock.end.of.day.report.wizard',
               'res_id': self.id,
               'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          })

          return {
               'type': 'ir.actions.act_url',
               'url': f'/web/content/{attachment.id}?download=true',
               'target': 'self',
          }

