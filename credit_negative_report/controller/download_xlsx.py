from odoo import http, fields
from odoo.http import request
import io
import re
import json
import xlsxwriter
from collections import defaultdict
from odoo.tools.float_utils import float_round
from odoo.tools import SQL


class ReportDownloadController(http.Controller):


    def _get_product_ids(self, compnay_ids, trade_term):        
        params = (
        True,
        compnay_ids,
        tuple(trade_term),
        )
        

        query = """
        SELECT 
            pp.id
        FROM 
            product_product pp
        LEFT JOIN 
            product_template pt ON pp.product_tmpl_id = pt.id
        LEFT JOIN 
            product_supplierinfo psi ON psi.product_tmpl_id = pt.id
        LEFT JOIN 
            res_partner rp ON rp.id = psi.partner_id
        WHERE 
            pp.active = %s
            AND pt.is_storable = TRUE
            AND (
                pt.company_id IS NULL OR pt.company_id IN %s
            )
            AND rp.trade_term IN %s
            AND psi.product_tmpl_id IS NOT NULL
        """
        
        request.env.cr.execute(query, params)
        product_ids = [row[0] for row in request.env.cr.fetchall()]

        return product_ids
    
    def _get_moves_in_res_past(self, where_clause, from_clause):
        query = SQL(
            """
            SELECT
                stock_move.company_id,
                stock_move.product_id,
                SUM(stock_move.quantity) AS total_quantity
            FROM %(from_clause)s
            WHERE %(where_clause)s
            GROUP BY
                stock_move.company_id,
                stock_move.product_id,
                stock_move.product_uom
            """,
            where_clause=where_clause,
            from_clause = from_clause

        )

        request.env.cr.execute(query)
        rows = request.env.cr.fetchall()

        moves_in_res_past = {
            (row[0], row[1]): (row[2])
            for row in rows
        }

        return moves_in_res_past
    
    def _get_moves_out_res_past(self, where_clause, from_clause):
        query = SQL(
            """
            SELECT
                stock_move.company_id,
                stock_move.product_id,
                SUM(stock_move.quantity) AS total_quantity
            FROM %(from_clause)s
            WHERE %(where_clause)s
            GROUP BY
                stock_move.company_id,
                stock_move.product_id,
                stock_move.product_uom
            """,
            where_clause=where_clause,
            from_clause = from_clause

        )

        request.env.cr.execute(query)
        rows = request.env.cr.fetchall()

        moves_out_res_past = {
            (row[0], row[1]): (row[2])
            for row in rows
        }

        return moves_out_res_past
    
    def _get_negative_products(self):
        company_product_data = defaultdict(lambda: defaultdict(list))

        company_ids = self.company_ids

        supplier_type = ['credit','consignment'] if self.supplier_type == "all" else [self.supplier_type]

        product_ids = self._get_product_ids(company_ids._ids, supplier_type)
        product_ids = request.env['product.product'].sudo().browse(product_ids)
        
        Warehouse = request.env['stock.warehouse'].sudo()
        
        location_ids = set(Warehouse.search(
                    [('company_id', 'in', company_ids.ids)]
                ).mapped('view_location_id').ids)
        
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = product_ids._get_domain_locations_new(location_ids)

        start_date = self.start_date
        end_date = self.end_date

        domain_move_in_done = [('location_id.usage', '!=', 'internal'),('state', '=', 'done'), ('date', '<=', end_date), ('date', '>=', start_date), ('product_id', 'in', product_ids.ids)] + domain_move_in_loc
        domain_move_out_done = [('location_dest_id.usage', '!=', 'internal'), ('state', '=', 'done'), ('date', '<=', end_date), ('date', '>=', start_date), ('product_id', 'in', product_ids.ids)] + domain_move_out_loc
    
        Move = request.env['stock.move'].with_context(active_test=False).sudo()

        _where_calc = Move._where_calc(domain_move_in_done)
        where_clause = _where_calc.where_clause
        from_clause = _where_calc.from_clause

        moves_in_res_past = self._get_moves_in_res_past(where_clause, from_clause)

        _where_calc = Move._where_calc(domain_move_out_done)
        where_clause = _where_calc.where_clause
        from_clause = _where_calc.from_clause
            
        moves_out_res_past = self._get_moves_out_res_past(where_clause, from_clause)

  
        for  product_id in product_ids:
            
            product = product_id

            origin_product_id = product._origin.id
            product_id = product.id
            categ_id = product.categ_id

            if origin_product_id:
                rounding = product.uom_id.rounding
                for company in self.company_ids:
                    
                    company = company.id
                
                    qty_available = moves_in_res_past.get((company, origin_product_id), 0.0) - moves_out_res_past.get((company, origin_product_id), 0.0)
                            
                    qty_available = float_round(qty_available, precision_rounding=rounding)

                    if qty_available < 0:
                         
                        company = request.env['res.company'].browse(company)
                        company_product_data[company][product_id].append({
                            'div_name': categ_id.name or '',
                            'dept_name': categ_id.department_name or '',
                            'sub_dept_name': categ_id.sub_department_name or '',
                            'store_code': company.pc_code or '',
                            'product_name': product.name or '',
                            'product_id': product.id or '',
                            'barcode': product.barcode or '',
                            'cogs': product.standard_price,
                            'stock_qty': qty_available,
                            'stock_amount': product.standard_price * qty_available,
                        })

        return company_product_data

    @http.route('/credit_negative_report/download/report', type='http', auth='user')
    def download_report(self,params=None, **kwargs):
            
            filters = json.loads(params or '{}')
            start_date = filters.get('start_date')
            end_date = filters.get('end_date')
            self.supplier_type = filters.get('supplier_type')
            company_ids = filters.get('company_ids')

            self.end_date = end_date
            self.start_date = start_date
            
            self.company_ids = request.env['res.company'].browse(company_ids)

            output = io.BytesIO()

            # Create a workbook and add a worksheet
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})

            # Define styles
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D3D3D3',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'
            })
            text_format = workbook.add_format({
                'border': 1,
                'valign': 'vcenter',
                'text_wrap': True
            })
            currency_format = workbook.add_format({
                'border': 1,
                'valign': 'vcenter',
                'num_format': '#,##0.00'
            })
            number_format = workbook.add_format({
                'border': 1,
                'valign': 'vcenter',
                'num_format': '#,##0'
            })

            grouped_products = self._get_negative_products()
            for company, line_detail in grouped_products.items():
                company_name = company.name or "NA"
                pc_code = company.pc_code or "NA"
                sheet_name_raw = f"{company_name}-{pc_code}"
                sheet_name = re.sub(r'[\\/*?:[\]]', '_', sheet_name_raw)[:31]
                sheet = workbook.add_worksheet(name=sheet_name)

                # Freeze header rows
                sheet.freeze_panes(2, 0)

                # Write company header
                sheet.merge_range('A1:K1', f"Company: {company_name} (Code: {pc_code})", header_format)

                # Write table headers
                headers = [
                    'No', 'Div Name', 'Dept Name', 'Sub-dept Name', 'Store code',
                    'Product ID', 'Barcode', 'Product Name',
                    'COGS', 'Stock Qty', 'Stock Amount'
                ]
                column_widths = [10, 20, 20, 25, 15, 15, 15, 30, 12, 12, 15]
                for col, (header, width) in enumerate(zip(headers, column_widths)):
                    sheet.write(1, col, header, header_format)
                    sheet.set_column(col, col, width)

                # Safe calculation for Sub-dept and Product Name column widths
                sub_dept_lengths = [
                    len(product['sub_dept_name'])
                    for division_products in line_detail.values()
                    for product in division_products
                ]
                max_sub_dept_name_length = max(sub_dept_lengths) + 5 if sub_dept_lengths else 30
                sheet.set_column(3, 3, max(25, max_sub_dept_name_length))

                product_name_lengths = [
                    len(product['product_name'])
                    for division_products in line_detail.values()
                    for product in division_products
                ]
                max_product_name_length = max(product_name_lengths) + 5 if product_name_lengths else 30
                sheet.set_column(6, 6, max(30, max_product_name_length))

                # Write all products from all divisions into this sheet
                row = 2
                product_index = 1
                for division_products in line_detail.values():
                    for product in division_products:
                        sheet.write(row, 0, product_index, number_format)
                        sheet.write(row, 1, product['div_name'], text_format)
                        sheet.write(row, 2, product['dept_name'], text_format)
                        sheet.write(row, 3, product['sub_dept_name'], text_format)
                        sheet.write(row, 4, product['store_code'], number_format)
                        sheet.write(row, 5, product['product_id'], number_format)
                        sheet.write(row, 6, product['barcode'], text_format)
                        sheet.write(row, 7, product['product_name'], text_format)
                        sheet.write(row, 8, product['cogs'], currency_format)
                        sheet.write(row, 9, product['stock_qty'], number_format)
                        sheet.write(row, 10, product['stock_amount'], currency_format)
                        row += 1
                        product_index += 1

            workbook.close()
            output.seek(0)
            content = output.read()

            formatted_name = f"Credit Negative Stock Report - {self.start_date} to {self.end_date}"

            # Return file response
            headers = [
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename={formatted_name}.xlsx'),
            ]
            return request.make_response(content, headers)
