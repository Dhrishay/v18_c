from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.tools import float_round
import base64
import io
import xlsxwriter
from odoo.http import request


class ReportDownloadWizard(models.TransientModel):
    _name = 'top.selling.wizard'
    _description = "Top Selling Wizard"

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, readonly=1)
    start_date = fields.Date(string='Start date', default=fields.Date.today(), required=1)
    end_date = fields.Date(string='End date', default=fields.Date.today() + relativedelta(days=1), required=1)
    no_product = fields.Integer('Number of Products', required=1, default=100)
    report_name = fields.Selection([('top_amount', 'Top Sale by Amount Report'),
                                    ('top_quantity', 'Top Sale by Quantity Report'), ],
                                   string='Report By', default='top_amount', required=1)
    report_type = fields.Selection([('pdf', 'PDF'), ('excel', 'Excel')], string='Report Type', default='excel', required=1)
    model = fields.Selection([('pos', 'POS'), ('sale', 'Sale'), ('both', 'Both')], string='Model', default='both', required=1)

    def print_report(self):
        datas = self.print_report_data()
        data = {
            'datas': datas,
            'store_no': self.company_id.pc_code,
            'store_name': self.company_id.name,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        print("data---------------------------",data)
        if self.report_type == 'pdf':
            return self.env.ref('lo_top_selling_product_report.action_top_selling_products_pdf').report_action(self, data=data)
        else:
            return self.env.ref('lo_top_selling_product_report.action_top_selling_products_xlsx').report_action(self, data=data)

    def print_report_data(self):
        if self.model == 'sale':
            return self.get_sale_data()
        elif self.model == 'pos':
            return self.get_pos_data()
        else:
            return self.get_combined_sale_pos_data()

    def get_sale_data(self):
        self.ensure_one()
        start = self.start_date.strftime('%Y-%m-%d 00:00:00')
        end = self.end_date.strftime('%Y-%m-%d 23:59:59')
        company_id = self.company_id.id
        order_by_column = "SUM(sol.product_uom_qty)" if self.report_name == 'top_quantity' else "SUM(sol.price_total)"
        query = f"""
            WITH vendor_ranked AS (
                SELECT
                    psi.product_tmpl_id,
                    r.name AS vendor_name,
                    r.vendor_code AS vendor_code,
                    ROW_NUMBER() OVER (
                        PARTITION BY psi.product_tmpl_id
                        ORDER BY 
                            CASE WHEN psi.company_id = {company_id} THEN 0 ELSE 1 END,
                            psi.id
                    ) AS rn
                FROM product_supplierinfo psi
                JOIN res_partner r ON r.id = psi.partner_id
            )
            SELECT 
                pp.default_code AS product_code,
                pp.barcode AS barcode,
                pt.name AS product_name,
                pc.department_name,
                pc.sub_department_name,
                pc.division_name,
                vr.vendor_name,
                vr.vendor_code,
                SUM(sol.product_uom_qty) AS total_quantity,
                SUM(sol.price_total) AS total_amount
            FROM sale_order_line sol
            JOIN sale_order so ON sol.order_id = so.id
            JOIN product_product pp ON sol.product_id = pp.id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            JOIN product_category pc ON pt.categ_id = pc.id
            LEFT JOIN vendor_ranked vr ON vr.product_tmpl_id = pt.id AND vr.rn = 1
            WHERE
                so.company_id = {company_id}
                AND so.date_order BETWEEN '{start}' AND '{end}'
                AND so.state IN ('sale', 'done')
                AND COALESCE(so.request_type, FALSE) = FALSE
                AND pp.active = TRUE
                AND pt.active = TRUE
            GROUP BY 
                pp.default_code, pp.barcode, pt.name, pc.department_name, pc.sub_department_name, pc.division_name, vr.vendor_name, vr.vendor_code
            ORDER BY {order_by_column} DESC
            LIMIT {self.no_product};
        """
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    def get_pos_data(self):
        self.ensure_one()
        start = self.start_date.strftime('%Y-%m-%d 00:00:00')
        end = self.end_date.strftime('%Y-%m-%d 23:59:59')
        company_id = self.company_id.id
        order_by_column = "SUM(pol.qty)" if self.report_name == 'top_quantity' else "SUM(pol.price_subtotal_incl)"

        query = f"""
            WITH vendor_ranked AS (
                SELECT
                    psi.product_tmpl_id,
                    r.name AS vendor_name,
                    r.vendor_code AS vendor_code,
                    ROW_NUMBER() OVER (
                        PARTITION BY psi.product_tmpl_id
                        ORDER BY 
                            CASE WHEN psi.company_id = {company_id} THEN 0 ELSE 1 END,
                            psi.id
                    ) AS rn
                FROM product_supplierinfo psi
                JOIN res_partner r ON r.id = psi.partner_id
            )
            SELECT 
                pp.default_code AS product_code,
                pp.barcode AS barcode,
                pt.name AS product_name,
                pc.department_name,
                pc.sub_department_name,
                pc.division_name,
                vr.vendor_name,
                vr.vendor_code,
                SUM(pol.qty) AS total_quantity,
                SUM(pol.price_subtotal_incl) AS total_amount
            FROM pos_order_line pol
            JOIN pos_order po ON pol.order_id = po.id
            JOIN product_product pp ON pol.product_id = pp.id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            JOIN product_category pc ON pt.categ_id = pc.id
            LEFT JOIN vendor_ranked vr ON vr.product_tmpl_id = pt.id AND vr.rn = 1
            WHERE
                po.company_id = {company_id}
                AND po.date_order BETWEEN '{start}' AND '{end}'
                AND po.state = 'done'
                AND pp.active = TRUE
                AND pt.active = TRUE
            GROUP BY 
                pp.default_code, pp.barcode, pt.name, pc.department_name, pc.sub_department_name, pc.division_name, vr.vendor_name, vr.vendor_code
            ORDER BY {order_by_column} DESC
            LIMIT {self.no_product};
        """
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    def get_combined_sale_pos_data(self):
        self.ensure_one()
        start = self.start_date.strftime('%Y-%m-%d 00:00:00')
        end = self.end_date.strftime('%Y-%m-%d 23:59:59')
        company_id = self.company_id.id

        order_by_column = "SUM(combined.total_quantity)" if self.report_name == 'top_quantity' else "SUM(combined.total_amount)"

        query = f"""
            WITH vendor_ranked AS (
                SELECT DISTINCT ON (psi.product_tmpl_id)
                    psi.product_tmpl_id,
                    r.name AS vendor_name,
                    r.vendor_code AS vendor_code
                FROM product_supplierinfo psi
                JOIN res_partner r ON r.id = psi.partner_id
                WHERE r.active IS TRUE
                ORDER BY 
                    psi.product_tmpl_id,
                    CASE WHEN psi.company_id = {company_id} THEN 0 ELSE 1 END,
                    psi.sequence ASC
            ),
            combined AS (
                -- Sale Order Data
                SELECT 
                    pp.id AS product_id,
                    pt.id AS product_tmpl_id,
                    pp.default_code,
                    pp.barcode,
                    pt.name AS product_name,
                    pc.department_name,
                    pc.sub_department_name,
                    pc.division_name,
                    SUM(sol.product_uom_qty) AS total_quantity,
                    SUM(sol.price_total) AS total_amount
                FROM sale_order_line sol
                JOIN sale_order so ON sol.order_id = so.id
                JOIN product_product pp ON sol.product_id = pp.id
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                JOIN product_category pc ON pt.categ_id = pc.id
                WHERE
                    so.company_id = {company_id}
                    AND so.date_order BETWEEN '{start}' AND '{end}'
                    AND so.state IN ('sale', 'done')
                    AND COALESCE(so.request_type, FALSE) = FALSE
                    AND pp.active = TRUE
                    AND pt.active = TRUE
                GROUP BY pp.id, pt.id, pp.default_code, pp.barcode, pt.name, pc.department_name, pc.sub_department_name, pc.division_name

                UNION ALL

                -- POS Order Data
                SELECT 
                    pp.id AS product_id,
                    pt.id AS product_tmpl_id,
                    pp.default_code,
                    pp.barcode,
                    pt.name AS product_name,
                    pc.department_name,
                    pc.sub_department_name,
                    pc.division_name,
                    SUM(pol.qty) AS total_quantity,
                    SUM(pol.price_subtotal_incl) AS total_amount
                FROM pos_order_line pol
                JOIN pos_order po ON pol.order_id = po.id
                JOIN product_product pp ON pol.product_id = pp.id
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                JOIN product_category pc ON pt.categ_id = pc.id
                WHERE
                    po.company_id = {company_id}
                    AND po.date_order BETWEEN '{start}' AND '{end}'
                    AND po.state = 'done'
                    AND pp.active = TRUE
                    AND pt.active = TRUE
                GROUP BY pp.id, pt.id, pp.default_code, pp.barcode, pt.name, pc.department_name, pc.sub_department_name, pc.division_name
            )

            SELECT 
                combined.default_code AS product_code,
                combined.barcode,
                combined.product_name,
                combined.department_name,
                combined.sub_department_name,
                combined.division_name,
                vr.vendor_name,
                vr.vendor_code,
                SUM(combined.total_quantity) AS total_quantity,
                SUM(combined.total_amount) AS total_amount
            FROM combined
            LEFT JOIN vendor_ranked vr ON vr.product_tmpl_id = combined.product_tmpl_id
            GROUP BY 
                combined.default_code,
                combined.barcode,
                combined.product_name,
                combined.department_name,
                combined.sub_department_name,
                combined.division_name,
                vr.vendor_name,
                vr.vendor_code
            ORDER BY {order_by_column} DESC
            LIMIT {self.no_product};
        """
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()


class NeverSoldXlsx(models.AbstractModel):
    _name = 'report.lo_top_selling_product_report.top_selling_products_xlsx'
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet('Never Sold Report')
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
            'align': 'center',
            'text_wrap': True
        })

        number_format = workbook.add_format({
            'border': 1,
            'valign': 'top',
            'align': 'right',
            'num_format': '#,##0.00'
        })

        store_name = data.get('store_name', '')
        store_no = data.get('store_no', '')
        start_date = data.get('start_date', '')
        end_date = data.get('end_date', '')
        datas = data.get('datas', [])

        sheet.merge_range('A1:K1', f"Store: {store_name} (Code: {store_no})", header_format)
        sheet.merge_range('A2:K2', f"Date: {start_date} to {end_date}", header_format)
        sheet.set_column('A:A', 5)
        sheet.set_column('B:F', 18)
        sheet.set_column('E:H', 15)
        sheet.set_column('I:I', 40)
        sheet.set_column('J:K', 18)

        headers = [
            'No', 'Div Name', 'Dept Name', 'Sub-dept Name', 'Vendor Code', 'Vendor Name',
            'Product ID', 'Barcode', 'Description', 'Sale Qty', 'Sale AMT'
        ]
        for col, header in enumerate(headers):
            sheet.write(4, col, header, header_format)

        row = 5
        for idx, item in enumerate(datas, 1):
            sheet.write(row, 0, idx, seq_format)
            sheet.write(row, 1, item.get('division_name', ''), text_format)
            sheet.write(row, 2, item.get('department_name', ''), text_format)
            sheet.write(row, 3, item.get('sub_department_name', ''), text_format)
            sheet.write(row, 4, item.get('vendor_code', ''), text_format)
            sheet.write(row, 5, item.get('vendor_name', ''), text_format)
            sheet.write(row, 6, item.get('product_code', ''), text_format)
            sheet.write(row, 7, item.get('barcode', ''), text_format)
            sheet.write(row, 8, item.get('product_name', {}).get('en_US', ''), text_format)
            sheet.write(row, 9, item.get('total_quantity', 0), number_format)
            sheet.write(row, 10, item.get('total_amount', 0), number_format)
            row += 1

        sheet.freeze_panes(5, 0)
