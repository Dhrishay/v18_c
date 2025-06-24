from odoo import models, fields, api
import logging
import xlsxwriter
import io
from datetime import datetime
from odoo.http import request, content_disposition
from odoo.tools import osutil

_logger = logging.getLogger(__name__)


class NeverSoldWizard(models.TransientModel):
    _name = 'never.sold.wizard'
    _description = 'Wizard for Never Sold Report'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    report_by = fields.Selection([
        ('all', 'All'),
        ('department', 'Department'),
        ('sub_department', 'Sub-Department'),
        ('division', 'Division'),
    ], string="Report By", default='all')
    vendor_report_by = fields.Selection([
        ('all', 'All'),
        ('vendor', 'By Vendor'),
    ], string="Report By", default='all')
    vendor_ids = fields.Many2many('res.partner', string='Vendor')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    export_format = fields.Selection([
        ('pdf', 'PDF'),
        ('xlsx', 'Excel'),
    ], string="Export Format", required=True)
    group_by = fields.Selection([
        ('category', 'Category'),
        ('vendor', 'vendor')], string="Group By")

    def action_download_report(self):
        if self.group_by == 'category':
            return self.print_category_report()
        else:
            return self.print_vendor_report()

    def get_order_by_field(self):
        if self.report_by == 'all':
            return "pc.division_name, pc.department_name, pc.sub_department_name"
        elif self.report_by == 'department':
            return "pc.department_name"
        elif self.report_by == 'sub_department':
            return "pc.sub_department_name"
        elif self.report_by == 'division':
            return "pc.division_name"
        return "pc.division_name, pc.department_name, pc.sub_department_name"

    def print_category_report(self):
        order_field = self.get_order_by_field()
        start_datetime = datetime.combine(self.start_date, datetime.min.time())
        end_datetime = datetime.combine(self.end_date, datetime.max.time())

        query = f"""
                SELECT 
                   pc.division_name as division,
                   pc.department_name as department,
                   pc.sub_department_name as sub_department,
                   pp.default_code as product_default_code,
                   pp.barcode as barcode,
                   pt.name as description
    
                FROM product_product pp
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                JOIN stock_quant sq ON sq.product_id = pp.id
                JOIN product_category pc ON pc.id = pt.categ_id
    
                WHERE sq.quantity > 0
                    AND sq.company_id = %s
                    AND pp.active = TRUE
                    AND pt.active = TRUE
                    AND pp.id NOT IN (
                        SELECT sol.product_id
                            FROM sale_order_line sol
                            JOIN sale_order so ON so.id = sol.order_id
                                WHERE so.state IN ('sale', 'done')
                                AND so.date_order BETWEEN %s AND %s
                                AND so.company_id = %s
                    UNION
                        SELECT pol.product_id
                            FROM pos_order_line pol
                            JOIN pos_order po ON po.id = pol.order_id
                                WHERE po.state IN ('paid', 'invoiced', 'done')
                                AND po.date_order BETWEEN %s AND %s
                                AND po.company_id = %s
                   )
    
                GROUP BY
                   pc.division_name,
                   pc.department_name,
                   pc.sub_department_name,
                   pp.default_code,
                   pp.barcode,
                   pt.name
                ORDER BY {order_field}
            """

        self.env.cr.execute(query, (
            self.company_id.id,
            start_datetime, end_datetime, self.company_id.id,
            start_datetime, end_datetime, self.company_id.id
        ))

        data = {
            'datas': self.env.cr.dictfetchall(),
            'store_no': self.company_id.pc_code,
            'store_name': self.company_id.name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'group_by': self.group_by
        }
        if self.export_format == 'pdf':
            return self.env.ref('lo_never_sold_report.action_lo_never_sold_report').report_action(self, data=data)
        else:
            return self.env.ref('lo_never_sold_report.action_lo_never_sold_report_xlsx').report_action(self, data=data)

    def print_vendor_report(self):
        start_datetime = datetime.combine(self.start_date, datetime.min.time())
        end_datetime = datetime.combine(self.end_date, datetime.max.time())

        vendor_filter_clause = ""
        vendor_filter_params = []

        if self.vendor_report_by == 'vendor':
            vendor_ids = tuple(self.vendor_ids.ids or [0])
            vendor_filter_clause = "AND psi.partner_id IN %s"
            vendor_filter_params.append(vendor_ids)

        vendor_subquery = """
            SELECT ps.id
            FROM product_supplierinfo ps
            WHERE ps.product_tmpl_id = pt.id
            ORDER BY
                CASE WHEN ps.partner_id IN (
                    SELECT id FROM res_partner WHERE company_id = %s
                ) THEN 0 ELSE 1 END,
                ps.sequence ASC
                LIMIT 1
        """

        query = f"""
            SELECT 
                rp.vendor_code as vendor_code,
                rp.name as vendor_name,
                pp.default_code as product_default_code,
                pp.barcode as barcode,
                pt.name as description

            FROM product_product pp
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            JOIN stock_quant sq ON sq.product_id = pp.id

            LEFT JOIN LATERAL (
                {vendor_subquery}
            ) AS selected_supplier ON TRUE
            LEFT JOIN product_supplierinfo psi ON psi.id = selected_supplier.id
            LEFT JOIN res_partner rp ON rp.id = psi.partner_id

            WHERE sq.quantity > 0
                AND sq.company_id = %s
                AND pp.active = TRUE
                AND pt.active = TRUE
                AND pp.id NOT IN (
                    SELECT sol.product_id
                    FROM sale_order_line sol
                    JOIN sale_order so ON so.id = sol.order_id
                    WHERE so.state IN ('sale', 'done')
                        AND so.date_order BETWEEN %s AND %s
                        AND so.company_id = %s
                UNION
                    SELECT pol.product_id
                    FROM pos_order_line pol
                    JOIN pos_order po ON po.id = pol.order_id
                    WHERE po.state IN ('paid', 'invoiced', 'done')
                        AND po.date_order BETWEEN %s AND %s
                        AND po.company_id = %s
                )
                {vendor_filter_clause}

            GROUP BY rp.vendor_code, rp.name, pp.default_code, pp.barcode, pt.name
            ORDER BY rp.name
        """
        params = [
                     self.company_id.id,
                     self.company_id.id,
                     start_datetime, end_datetime, self.company_id.id,
                     start_datetime, end_datetime, self.company_id.id,
                 ] + vendor_filter_params
        self.env.cr.execute(query, params)
        data = {
            'datas': self.env.cr.dictfetchall(),
            'store_no': self.company_id.pc_code,
            'store_name': self.company_id.name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'group_by': self.group_by,
            'vendor_report_by': self.vendor_report_by,
            'vendor_ids': self.vendor_ids.ids,
        }
        if self.export_format == 'pdf':
            return self.env.ref('lo_never_sold_report.action_lo_never_sold_report').report_action(self, data=data)
        else:
            return self.env.ref('lo_never_sold_report.action_lo_never_sold_report_xlsx').report_action(self, data=data)


class NeverSoldXlsx(models.AbstractModel):
    _name = 'report.lo_never_sold_report.report_never_sold_xlsx'
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, wizard):
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
            'align': 'center',
            'text_wrap': True
        })
        store_name = data.get('store_name', '')
        store_no = data.get('store_no', '')
        start_date = data.get('start_date', '')
        end_date = data.get('end_date', '')
        datas = data.get('datas', [])

        if data.get('group_by') == 'category':
            sheet.merge_range('A1:H1', f"Store: {store_name} (Code: {store_no})", header_format)
            sheet.merge_range('A2:H2', f"Date: {start_date} to {end_date}", header_format)
            sheet.set_column('A:A', 5)
            sheet.set_column('B:D', 18)
            sheet.set_column('E:F', 15)
            sheet.set_column('G:G', 40)
            sheet.set_column('H:H', 12)

            headers = [
                'No', 'Div Name', 'Dept Name', 'Sub-dept Name',
                'Product ID', 'Barcode', 'Description', 'Store No'
            ]
            for col, header in enumerate(headers):
                sheet.write(4, col, header, header_format)
            row = 5
            for idx, item in enumerate(datas, 1):
                sheet.write(row, 0, idx, seq_format)
                sheet.write(row, 1, item.get('division', ''), text_format)
                sheet.write(row, 2, item.get('department', ''), text_format)
                sheet.write(row, 3, item.get('sub_department', ''), text_format)
                sheet.write(row, 4, item.get('product_default_code', ''), text_format)
                sheet.write(row, 5, item.get('barcode', ''), text_format)
                sheet.write(row, 6, item.get('description', {}).get('en_US', ''), text_format)
                sheet.write(row, 7, store_no, text_format)
                row += 1
        else:
            sheet.merge_range('A1:G1', f"Store: {store_name} (Code: {store_no})", header_format)
            sheet.merge_range('A2:G2', f"Date: {start_date} to {end_date}", header_format)
            sheet.set_column('A:A', 5)
            sheet.set_column('B:D', 18)
            sheet.set_column('E:E', 15)
            sheet.set_column('F:F', 40)
            sheet.set_column('G:G', 15)
            headers = [
                'No', 'Vendor Code', 'Vendor Name',
                'Product ID', 'Barcode', 'Description', 'Store No'
            ]
            for col, header in enumerate(headers):
                sheet.write(4, col, header, header_format)
            row = 5
            for idx, item in enumerate(datas, 1):
                sheet.write(row, 0, idx, seq_format)
                sheet.write(row, 1, item.get('vendor_code', ''), text_format)
                sheet.write(row, 2, item.get('vendor_name', ''), text_format)
                sheet.write(row, 3, item.get('product_default_code', ''), text_format)
                sheet.write(row, 4, item.get('barcode', ''), text_format)
                sheet.write(row, 5, item.get('description', {}).get('en_US', ''), text_format)
                sheet.write(row, 6, store_no, text_format)
                row += 1
        sheet.freeze_panes(5, 0)
