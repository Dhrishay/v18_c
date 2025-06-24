from odoo import models, fields, api, _
from collections import defaultdict
from collections import defaultdict
from odoo.exceptions import UserError
from urllib.parse import urlencode
from odoo.tools.float_utils import float_round
import json
from odoo.tools import SQL

class CreditNegativeReport(models.AbstractModel):
    _name = 'report.credit_negative_report.credit_negative_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['credit.negative.stock.wizard'].sudo().browse(docids)

        company_product_data = docs._get_negative_products()

        return {
            'docs': docs,
            'company_grouped': company_product_data,
        }

class CreditNegativeReportWizard(models.TransientModel):
    _name = 'credit.negative.stock.wizard'
    _description = 'Wizard for Never Sold Report'

    start_date = fields.Datetime(string="Start Date", required=True)
    end_date = fields.Datetime(string="End Date", required=True)
    supplier_type = fields.Selection([
        ('all', 'All'),
        ('credit', 'Credit'),
        ('consignment', 'Consignment')
    ], string="Supplier Type", required=True)
    # store_codes = fields.Char(string='Store Codes', compute='_compute_store_codes')
    company_ids = fields.Many2many('res.company', string='Companies', required=True, domain=lambda self: [('id', 'in', self.env.user.company_ids.ids)])
    export_format = fields.Selection([
        ('pdf', 'PDF'),
        ('xlsx', 'Excel'),
    ], string="Print Out", required=True)
    has_child = fields.Boolean(string='Branch')  # Manual field
    show_has_child_field = fields.Boolean(string='Show Branch Field', store=True,compute="_compute_show_has_branch")

    @api.depends('company_ids')
    def _compute_show_has_branch(self):
        for record in self:
            record.show_has_child_field = any(company.child_ids for company in record.company_ids)

    def action_download_report(self):
        if self.export_format == 'pdf':
            return self.env.ref('credit_negative_report.action_credit_negative_report').report_action(self)
        elif self.export_format == 'xlsx':
            return self._export_xlsx()

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

        
        self.env.cr.execute(query, params)
        product_ids = [row[0] for row in self.env.cr.fetchall()]
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

        self.env.cr.execute(query)
        rows = self.env.cr.fetchall()

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

        self.env.cr.execute(query)
        rows = self.env.cr.fetchall()

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
        product_ids = self.env['product.product'].sudo().browse(product_ids)
        
        Warehouse = self.env['stock.warehouse'].sudo()
        
        location_ids = set(Warehouse.search(
                    [('company_id', 'in', company_ids.ids)]
                ).mapped('view_location_id').ids)
        
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = product_ids._get_domain_locations_new(location_ids)
        domain_quant = [('product_id', 'in', product_ids.ids)] + domain_quant_loc

        start_date = self.start_date
        end_date = self.end_date

        domain_move_in_done = [('location_id.usage', '!=', 'internal'), ('state', '=', 'done'), ('date', '<=', end_date), ('date', '>=', start_date), ('product_id', 'in', product_ids.ids)] + domain_move_in_loc
        domain_move_out_done = [('location_dest_id.usage', '!=', 'internal'), ('state', '=', 'done'), ('date', '<=', end_date), ('date', '>=', start_date), ('product_id', 'in', product_ids.ids)] + domain_move_out_loc

        Move = self.env['stock.move'].with_context(active_test=False).sudo()
        Quant = self.env['stock.quant'].with_context(active_test=False).sudo()

        _where_calc = Quant._where_calc(domain_quant)
        where_clause = _where_calc.where_clause
        from_clause = _where_calc.from_clause
    
        _where_calc = Move._where_calc(domain_move_in_done)
        where_clause = _where_calc.where_clause
        from_clause = _where_calc.from_clause

        moves_in_res_past = self._get_moves_in_res_past(where_clause, from_clause)

        _where_calc = Move._where_calc(domain_move_out_done)
        where_clause = _where_calc.where_clause
        from_clause = _where_calc.from_clause
        
        moves_out_res_past = self._get_moves_out_res_past(where_clause, from_clause)
        
        for product_id in product_ids:
            
            product = product_id

            origin_product_id = product._origin.id
            product_id = product.id
            
            if origin_product_id:
                categ_id = product.categ_id
                rounding = product.uom_id.rounding
                for company in self.company_ids:
                    company = company.id

                    qty_available = moves_in_res_past.get((company, origin_product_id), 0.0) - moves_out_res_past.get((company, origin_product_id), 0.0)


                    qty_available = float_round(qty_available, precision_rounding=rounding)

                    if qty_available < 0:
                        company = self.env['res.company'].browse(company)
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

    

    def _export_xlsx(self):
        company_ids = (self.company_ids.child_ids | self.company_ids) if self.has_child else self.company_ids

        params = {'start_date': str(self.start_date), 'end_date': str(self.end_date), 'supplier_type': self.supplier_type, 'company_ids': company_ids.ids}
        query = urlencode({'params': json.dumps(params)})

        return {
            'type': 'ir.actions.act_url',
            'url': f'/credit_negative_report/download/report?{query}',
            'target': 'self',
        }
