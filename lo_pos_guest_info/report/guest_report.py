# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools


class ReportGuestDetail(models.Model):
    _name = 'report.guest.detail'
    _description = "Guest Detail Report"
    _auto = False
    _order = 'date desc'
    _rec_name = 'order_id'

    # guest details fields
    date = fields.Datetime(
        string='Order Date', readonly=True
    )
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string="Gender")
    order_id = fields.Many2one(
        'pos.order', string='Order'
    )
    config_id = fields.Many2one(
        'pos.config', string='Point of Sale'
    )
    company_id = fields.Many2one(
        'res.company', string='Company'
    )
    session_id = fields.Many2one(
        'pos.session', string='Session'
    )
    user_id = fields.Many2one(
        'res.users', string='Cashier'
    )
    country_id = fields.Many2one('res.country')
    guest_count = fields.Integer('Total Count')
    no_of_male = fields.Char('Male')
    no_of_female = fields.Char('Female')
    table_id = fields.Many2one(
        'restaurant.table', string='Table'
    )
    age = fields.Integer(string="Guest Age")
    guest_age_range = fields.Selection([
        ('below_20', 'Below 20'), ('20_25', '20-25'),
        ('26_30', '26-30'), ('31_35', '31-35'),
        ('36_40', '36-40'), ('41_45', '41-45'),
        ('46_50', '46-50'), ('above_50', 'Above 50')],
        string="Age", compute="_compute_guest_age_range",
        store=True, readonly=False
    )

    # pos order fields
    partner_id = fields.Many2one(
        'res.partner', string='Customer',
        readonly=True
    )
    product_id = fields.Many2one(
        'product.product', string='Product',
        readonly=True
    )
    product_tmpl_id = fields.Many2one(
        'product.template', string='Product Template',
        readonly=True
    )
    state = fields.Selection(
        [('draft', 'New'), ('paid', 'Paid'),
        ('done', 'Posted'),
        ('invoiced', 'Invoiced'), ('cancel', 'Cancelled')],
        string='Status', readonly=True
    )
    price_total = fields.Float(
        string='Total Price', readonly=True
    )
    price_sub_total = fields.Float(
        string='Subtotal w/o discount', readonly=True
    )
    price_subtotal_excl = fields.Float(
        string='Subtotal w/o Tax', readonly=True
    )
    total_discount = fields.Float(
        string='Total Discount', readonly=True
    )
    average_price = fields.Float(
        string='Average Price', readonly=True,
        aggregator="avg"
    )
    nbr_lines = fields.Integer(
        string='Sale Line Count', readonly=True
    )
    product_qty = fields.Integer(
        string='Product Quantity', readonly=True
    )
    journal_id = fields.Many2one(
        'account.journal', string='Journal',
        readonly=True
    )
    delay_validation = fields.Integer(
        string='Delay Validation', readonly=True
    )
    product_categ_id = fields.Many2one(
        'product.category', string='Product Category',
        readonly=True
    )
    pos_categ_id = fields.Many2one(
        'pos.category', string='Point of Sale Category',
        readonly=True
    )
    invoiced = fields.Boolean(readonly=True)
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist',
        readonly=True
    )
    margin = fields.Float(string='Margin', readonly=True)
    payment_method_id = fields.Many2one(
        'pos.payment.method', string='Payment Method',
        readonly=True
    )
   
    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                WITH payment_method_by_order_line AS (
                    SELECT
                        pol.id AS pos_order_line_id,
                        (array_agg(pm.payment_method_id))[1] AS payment_method_id
                    FROM pos_order_line pol
                    LEFT JOIN pos_order po ON (po.id = pol.order_id)
                    LEFT JOIN pos_payment pm ON (pm.pos_order_id=po.id)
                    GROUP BY pol.id
                )
                SELECT
                    -- Fields from guest_detail
                    g.id AS id,
                    g.create_date AS date,
                    g.gender AS gender,
                    g.order_id AS order_id,
                    g.config_id AS config_id,
                    g.company_id AS company_id,
                    g.session_id AS session_id,
                    g.user_id AS user_id,
                    g.country_id AS country_id,
                    g.age AS age,
                    g.guest_age_range AS guest_age_range,
                    CASE
                        WHEN g.gender = 'male' THEN 1
                        ELSE 0
                    END AS no_of_male,
                    CASE
                        WHEN g.gender = 'female' THEN 1
                        ELSE 0
                    END AS no_of_female,
                    (CASE WHEN g.gender = 'male' THEN 1 ELSE 0 END + CASE WHEN g.gender = 'female' THEN 1 ELSE 0 END) AS guest_count,
                    po.table_id AS table_id,

                    -- Fields from pos_order_line
                    1 AS nbr_lines, -- number of lines in order line is always 1
                    l.qty AS product_qty,
                    l.qty * l.price_unit / COALESCE(NULLIF(s.currency_rate, 0), 1.0) AS price_sub_total,
                    l.price_unit AS price_unit,
                    ROUND((l.price_subtotal) / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END, cu.decimal_places) AS price_subtotal_excl,
                    ROUND((l.price_subtotal_incl) / COALESCE(NULLIF(s.currency_rate, 0), 1.0), cu.decimal_places) AS price_total,
                    (l.qty * l.price_unit) * (l.discount / 100) / COALESCE(NULLIF(s.currency_rate, 0), 1.0) AS total_discount,
                    l.qty * u.factor AS uom_qty,
                    CASE
                        WHEN l.qty * u.factor = 0 THEN NULL
                        ELSE (l.qty * l.price_unit / COALESCE(NULLIF(s.currency_rate, 0), 1.0)) / (l.qty * u.factor)::decimal
                    END AS average_price,
                    cast(to_char(date_trunc('day',s.date_order) - date_trunc('day',s.create_date),'DD') AS INT) AS delay_validation,
                    s.partner_id AS partner_id,
                    s.state AS state,
                    s.user_id AS sales_user_id,
                    s.pricelist_id,

                    s.sale_journal AS journal_id,
                    l.product_id AS product_id,
                    pt.categ_id AS product_categ_id,
                    p.product_tmpl_id,
                   
                    s.account_move IS NOT NULL AS invoiced,
                    pc.id AS pos_categ_id,
                    l.price_subtotal - COALESCE(l.total_cost,0) / COALESCE(NULLIF(s.currency_rate, 0), 1.0) AS margin,
                   
                    pm.payment_method_id AS payment_method_id

                FROM guest_detail g
                LEFT JOIN pos_order po ON po.id = g.order_id
                LEFT JOIN pos_order_line l ON l.order_id = po.id
                LEFT JOIN pos_order s ON s.id = l.order_id
                LEFT JOIN product_product p ON l.product_id = p.id
                LEFT JOIN product_template pt ON p.product_tmpl_id = pt.id
                LEFT JOIN uom_uom u ON u.id = pt.uom_id
                LEFT JOIN pos_session ps ON ps.id = s.session_id
                LEFT JOIN res_company co ON s.company_id = co.id
                LEFT JOIN res_currency cu ON co.currency_id = cu.id
                LEFT JOIN payment_method_by_order_line pm ON pm.pos_order_line_id = l.id
                LEFT JOIN pos_payment_method ppm ON pm.payment_method_id = ppm.id
                LEFT JOIN pos_category_product_template_rel pcpt ON pt.id = pcpt.product_template_id
                LEFT JOIN pos_category pc ON pcpt.pos_category_id = pc.id
            )
        """)

