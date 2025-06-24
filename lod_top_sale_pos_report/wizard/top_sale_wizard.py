from odoo import models ,fields
from datetime import datetime,timedelta
from collections import defaultdict
import re
class TopsaleWizard(models.TransientModel):
    _name = 'lod.top.sale.report'
    _description = "lod report top sale"

    start_at = fields.Datetime('Start At')
    end_at = fields.Datetime('End At')
    config_ids = fields.Many2many('pos.config', string='POS')


    def print_sale_report_xlsx(self): 
        datas = {
        'model': 'lod.top.sale.report',
        'form': self.read()[0]
        }   
        return self.env.ref("lod_top_sale_pos_report.product_topsale_report").report_action(
            self,data=datas
        )


class TopsaleDetails(models.AbstractModel):
    _name = "report.lod_top_sale_pos_report.top_sale_xlsx"
    _inherit = "report.report_xlsx.abstract"

 

    def generate_xlsx_report(self, workbook, data, objs):
        data_form = data.get('form')
        config_ids = data_form.get('config_ids', [])
        domain = [
            ('order_id.date_order', '>=', data_form['start_at']),
            ('order_id.date_order', '<=', data_form['end_at']),
            ('order_id.session_id.config_id', 'in', config_ids),
        ]

        lines = self.env['pos.order.line'].search(domain)
         

       

        my_format = workbook.add_format(
            {
                'num_format':'#,##0.00', 
                "bold": True,
                "font_size": 10,
                "font": "Arial",
                "text_wrap": False,
                "border": True,
                "align": "right",
                }
            )
        bold = workbook.add_format(
            {
                "bold": True,
                "font_size": 14,
                "font": "Arial",
                "text_wrap": True,
                "border": True,
                "align": "center",
            }
        )
        boldr = workbook.add_format(
            {
                "bold": True,
                "font_size": 10,
                "font": "Arial",
                "text_wrap": True,
                "border": True,
                "align": "right",
            }
        )
        boldd = workbook.add_format(
            {
                "bold": True,
                "font_size": 10,
                "font": "Arial",
                "text_wrap": True,
                "border": True,
                "align": "center",
            }
        ) 
        
        cell = workbook.add_format(
            {
                "bold": True,
                "font_size": 10,
                "font": "Arial",
                "text_wrap": True,
                "border": True,
                "align": "left", 
            })
        cells = workbook.add_format(
            {
                "bold": True,
                "font_size": 10,
                "font": "Arial",
                "text_wrap": True,
                "border": True,
                "align": "center", 
            })
        celll = workbook.add_format(
            {
                "bold": True,
                "font_size": 10,
                "font": "Arial",
                "text_wrap": True,
                "border": True,
                "align": "center", 
            }
        )
        dates_format = workbook.add_format(
            {
                "bold": True,
                "font_size": 10,
                "font": "Arial",
                "text_wrap": False,
                "border": False,
                "align": "right",
            }
        )
        format = workbook.add_format(
            {
                "bold": True,
                "font_size": 10,
                "font": "Arial",
                "text_wrap": False,
                "border": False,
                "align": "left",
            }
        )
        text_align = workbook.add_format(
            {
                "bold": False,
                "font_size": 10,
                "font": "Arial",
                "text_wrap": False,
                "border": True,
                "align": "right",
            }
        )
        # Create worksheet
        sheet = workbook.add_worksheet('Top Sale Report')
        # Optional: Set column widths
        sheet.set_column('A:A', 5)
        sheet.set_column('B:B', 35)
        sheet.set_column('E:F', 30) 
        sheet.merge_range(1, 0, 1, 5, 'Top Sale Report', bold) 
        start_at = datetime.fromisoformat(data_form['start_at']) + timedelta(hours=7)
        end_at = datetime.fromisoformat(data_form['end_at']) + timedelta(hours=7) 
        sheet.write(2, 4, 'Start At : ' + start_at.strftime('%Y-%m-%d %H:%M:%S'), cell)
        sheet.write(2, 5, 'End At : ' + end_at.strftime('%Y-%m-%d %H:%M:%S'), cell)
        sheet.write(3, 0, 'No', celll)
        sheet.write(3, 1, 'Product', cell)
        sheet.write(3, 2, 'Size', cells)
        sheet.write(3, 3, 'Quantity', boldr)
        sheet.write(3, 4, 'Price Unit', boldr)
        sheet.write(3, 5, 'Total Amount', boldr) 
        row = 4
        no = 1
        product_summary = defaultdict(lambda: {'qty': 0, 'amount': 0, 'price_unit': 0})

        for line in lines:
            product = line.product_id
            display_name = product.display_name or ''

            # แยกชื่อ + ขนาดจากชื่อเต็ม (เช่น "GAGA Overload (M, 50%)")
            match = re.match(r"^(.*?)\s*\((.*?)\)$", display_name)
            name = display_name.strip()
            size = ''

            if match:
                name = match.group(1).strip()
                inside = match.group(2).strip()
                parts = [x.strip() for x in inside.split(',')]
                for part in parts:
                    if part.upper() in ['S', 'M', 'L']:
                        size = part.upper()

            key = (name, size)

            product_summary[key]['qty'] += line.qty
            product_summary[key]['price_unit'] = line.price_unit
            product_summary[key]['amount'] += line.price_subtotal_incl

        for (product_name, size), summary in sorted(product_summary.items(), key=lambda x: x[1]['amount'], reverse=True):
            price_unit = summary['amount'] / summary['qty'] if summary['qty'] else 0

            sheet.write(row, 0, no, boldd)
            sheet.write(row, 1, product_name, cell)
            sheet.write(row, 2, size, cell)
            sheet.write(row, 3, summary['qty'], my_format)
            sheet.write(row, 4, summary['price_unit'], my_format)
            sheet.write(row, 5, summary['amount'], my_format)

            row += 1
            no += 1