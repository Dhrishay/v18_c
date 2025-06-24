# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Laoodoo
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ReceiptDesignCustom(models.Model):
    _name = "receipt.design.custom"
    _rec_name = "name"
    _description = "Receipt Design (Custom)"

    name = fields.Char(string="Name", required=True)
    receipt_design_text = fields.Text(string='Description', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    receipt_type = fields.Selection(
        [('res_bar', 'Restaurant/Bar'), ('order', 'Order'), ('res_bar_sticker', 'Restaurant/Bar(sticker)')],
        required=True)
    pos_printers = fields.One2many('pos.printer', 'receipt_design', string='Pos Printer')
    pos_receipt_printer = fields.One2many('pos.config', 'receipt_design', string='Pos Receipt Printer')

    def write(self, vals):
        # Update records based on the new `receipt_design_text`
        if 'receipt_design_text' in vals:
            new_text = vals['receipt_design_text']
            for record in self:
                # Update related `pos.printer` records
                if record.pos_printers:
                    record.pos_printers.write(
                        {'receipt_design_text': new_text})

                # Update related `pos.config` records
                if record.pos_receipt_printer:
                    record.pos_receipt_printer.write(
                        {'receipt_design_text': new_text})

        # Call the super to ensure normal `write` functionality
        return super(ReceiptDesignCustom, self).write(vals)

    @api.model
    def _load_pos_data_domain(self):
        return []

    @api.model
    def _load_pos_data_fields(self):
        return ['name', 'receipt_design_text', 'company_id', 'receipt_type']

    def _load_pos_data(self, data):
        domain = self._load_pos_data_domain()
        fields = self._load_pos_data_fields()
        return {
            'data': self.search_read(domain, fields, load=False),
            'fields': self._load_pos_data_fields(),
        }

    # Below method for Demo Data of the Order Receipt as well as Bar/Rest Receipt

    @api.model
    def _create_sticker_design(self):
        record_data = {}
        record_data['name'] = "Restaurant/bar (Sticker Design)"
        record_data['company_id'] = self.env.company.id
        record_data['receipt_type'] = 'res_bar_sticker'
        record_data['receipt_design_text'] = """
                <div t-foreach="changedlines" t-as="line" t-key="change_index">
                    <t t-foreach="Array.from({length: line.qty}, (_, i) => i + 1)" t-as="qty_index" t-key="qty_index">
                        SIZE 40 mm, 20 mm@
                        GAP 2 mm, 0 mm@
                        DIRECTION 1@
                        BEEP@
                        CLS@
                        <t t-set="y_pos" t-value="10" />
                        [LAYOUT]@
                        TEXT 140,<t t-esc="y_pos"/>,"2",0,1,1,"<t t-esc='qty_index'/>/<t t-esc='line.qty'/>"@
                        <t t-if="line.order_id">
                            TEXT 220,<t t-esc="y_pos"/>,"2",0,1,1,"#<t t-esc='line.order_id.tracking_number'/>"@
                        </t>
                        <t t-set="y_pos" t-value="y_pos + 30" />
                        <t t-if="line.full_product_name">
                            <t t-set="chunk_size" t-value="20"/>
                            <t t-foreach="Array.from({length: Math.ceil(line.full_product_name.length / chunk_size)}, (_, i) => i * chunk_size)" t-as="i" t-key="i">
                                TEXT 15,<t t-esc="y_pos"/>,"2",0,1,1,"<t t-esc="line.full_product_name.slice(i, i + chunk_size)"/>"@
                                <t t-set="y_pos" t-value="y_pos + 20" />
                            </t>
                        </t>
                        TEXT 15,<t t-esc="y_pos"/>,"2",0,1,1,"--------------------"@
                        <t t-set="y_pos" t-value="y_pos + 20" />
                        <!-- Sticker Note -->
                        <t t-if="line.sticker_note">
                            TEXT 15,<t t-esc="y_pos"/>,"2",0,1,1,"<t t-esc='line.sticker_note.replace("\n", ", ")'/>"@
                            <t t-set="y_pos" t-value="y_pos + 20" />
                        </t>
                        <t t-set="y_pos" t-value="120" />
                        <!-- Symbol -->
                        <t t-if="line.price_subtotal_incl">
                            TEXT 15,<t t-esc="y_pos"/>,"2",0,1,1,"<t t-esc='order.company_id.currency_id.symbol'/> <t t-esc='line.price_subtotal_incl'/>"@
                        </t>
                        <t t-if="line.sticker_note">
                            TEXT 150,<t t-esc="y_pos"/>,"2",0,1,1,"<t t-esc='line.sticker_note.replace("\n", ", ")'/>"@
                        </t>
                        PRINT 1@
                    </t>
                </div>
        """
        self.create(record_data)

    @api.model
    def _create_sticker_design_topping(self):
        record_data = {}
        record_data['name'] = "Topping Restaurant/bar (Sticker Design)"
        record_data['company_id'] = self.env.company.id
        record_data['receipt_type'] = 'res_bar_sticker'
        record_data['receipt_design_text'] = """
            <div t-foreach="changedlines" t-as="line" t-key="change_index">
                <t t-foreach="Array.from({length: line.qty}, (_, i) => i + 1)" t-as="qty_index" t-key="qty_index">
                SIZE 40 mm, 20 mm@
                GAP 2 mm, 0 mm@
                DIRECTION 1@
                BEEP@
                CLS@
                    <t t-set="y_pos" t-value="10" />
                    [LAYOUT]@
                    TEXT 140,<t t-esc="y_pos"/>,"2",0,1,1,"<t t-esc='qty_index'/>/<t t-esc='line.qty'/>"@
                    <t t-if="line.order_id">
                        TEXT 220,<t t-esc="y_pos"/>,"2",0,1,1,"#<t t-esc='line.order_id.tracking_number'/>"@
                    </t>
                    <t t-set="y_pos" t-value="y_pos + 30" />
                    <t t-if="line.full_product_name">
                        <t t-set="chunk_size" t-value="20"/>
                        <t t-foreach="Array.from({length: Math.ceil(line.full_product_name.length / chunk_size)}, (_, i) => i * chunk_size)" t-as="i" t-key="i">
                            TEXT 15,<t t-esc="y_pos"/>,"2",0,1,1,"<t t-esc="line.full_product_name.slice(i, i + chunk_size)"/>"@
                            <t t-set="y_pos" t-value="y_pos + 20" />
                        </t>
                    </t>
                    TEXT 15,<t t-esc="y_pos"/>,"1.5",0,1,1,"--------------------"@
                    <t t-set="y_pos" t-value="y_pos + 20" />
                    <!-- Sticker Note -->
                    <t t-if="line.note">
                        <t t-set="chunk_size" t-value="20"/>
                        <t t-foreach="Array.from({length: Math.ceil(line.note.replace('\n', ', ').length / chunk_size)}, (_, i) => i * chunk_size)" t-as="i" t-key="i">
                            TEXT 15,<t t-esc="y_pos"/>,"1.5",0,1,1,"<t t-esc="line.note.replace('\n', ', ').slice(i, i + chunk_size)"/>"@
                            <t t-set="y_pos" t-value="y_pos + 20" />
                        </t>
                    </t>
                    <t t-if="line.line_topping_ids">
                        <t t-set="tp_code" t-value="'Tip: '" />
                        <t t-set="tp_code_coma" t-value="','" />
                        <t t-foreach="line.line_topping_ids" t-as="tip" t-key="tip">
                            <t t-if="tip.topping_code">
                                <t t-set="tp_code" t-value="tp_code + tip.topping_code + tp_code_coma" />
                            </t>
                        </t>
                        <t t-if="tp_code">
                            TEXT 15,<t t-esc="y_pos"/>,"1.5",0,1,1,"<t t-esc='tp_code'/>"@
                        </t>
                    </t>
                    <t t-set="y_pos" t-value="140" />
                    <!-- Symbol -->
                    <t t-if="line.price_subtotal_incl">
                        TEXT 15,<t t-esc="y_pos"/>,"2",0,1,1,"<t t-esc='order.company_id.currency_id.symbol'/> <t t-esc='line.price_subtotal_incl'/>"@
                    </t>
                    <t t-if="line.sticker_note">
                        TEXT 200,<t t-esc="y_pos"/>,"2",0,1,1,"<t t-esc='line.sticker_note.replace("\n", ", ")'/>"@
                    </t>
                    PRINT 1@
                </t>
            </div>
        """
        self.create(record_data)

    @api.model
    def _create_order_receipt_design_1(self):
        record_data = {}
        record_data['name'] = "Order Receipt Design 1"
        record_data['company_id'] = self.env.company.id
        record_data['receipt_type'] = 'order'
        record_data['receipt_design_text'] = """
        <div class="pos-receipt p-2">
            <t t-set="showTaxGroupLabels" t-value="doesAnyOrderlineHaveTaxLabel()"/>
            <ReceiptHeader data="props.data.headerData" />
            <OrderWidget t-if="props.data.orderlines?.length" lines="props.data.orderlines" t-slot-scope="scope" generalNote="props.data.generalNote or ''" screenName="props.data.screenName">
                <t t-set="line" t-value="scope.line"/>
                <Orderline basic_receipt="props.basic_receipt" line="omit(scope.line, 'customerNote')" class="{ 'px-0': true }" showTaxGroupLabels="showTaxGroupLabels">
                    <li t-if="line.customerNote" class="customer-note w-100 p-2 my-1 rounded text-break">
                        <i class="fa fa-sticky-note me-1" role="img" aria-label="Customer Note" title="Customer Note"/>
                        <t t-esc="line.customerNote" />
                    </li>
                </Orderline>
            </OrderWidget>
            <t t-if="!props.basic_receipt">
                <div t-if="props.data.tax_details.length > 0" class="pos-receipt-taxes">
                    <div class="text-center">-------Order Receipt Design 1-------</div>
                    <div class="d-flex">
                        <span t-if="showTaxGroupLabels" class="me-2" style="visibility: hidden;">A</span>
                        <span class="fw-bolder">Untaxed Amount</span>
                        <span t-esc="props.formatCurrency(props.data.total_without_tax)" class="ms-auto"/>
                    </div>

                    <div t-foreach="props.data.tax_details" t-as="tax" t-key="tax.id" class="d-flex">
                        <t t-if="showTaxGroupLabels">
                            <span t-if="tax.tax_group_id.pos_receipt_label" t-esc="tax.tax_group_id.pos_receipt_label" class="me-2"/>
                            <span t-else="" class="me-2" style="visibility: hidden;">A</span>
                        </t>
                        <span>
                            <span t-esc="tax.name"/>
                            on
                            <span t-esc="props.formatCurrency(tax.base)"/>
                        </span>
                        <span t-esc="props.formatCurrency(tax.amount)" class="ms-auto"/>
                    </div>
                </div>

                <!-- Total -->
                <div class="text-center">-------Order Receipt Design 1------</div>
                <div class="pos-receipt-amount">
                    TOTAL
                    <span t-esc="props.formatCurrency(props.data.amount_total)" class="pos-receipt-right-align"/>
                </div>
                <t t-if="props.data.rounding_applied">
                    <div class="pos-receipt-amount">
                    Rounding
                    <span t-esc='props.formatCurrency(props.data.rounding_applied)' class="pos-receipt-right-align"/>
                    </div>
                    <div class="pos-receipt-amount">
                    To Pay
                    <span t-esc='props.formatCurrency(props.data.amount_total + props.data.rounding_applied)' class="pos-receipt-right-align"/>
                </div>
                </t>

                <!-- Payment Lines -->

                <div class="paymentlines text-start" t-foreach="props.data.paymentlines" t-as="line" t-key="line_index">
                    <t t-esc="line.name" />
                    <span t-esc="props.formatCurrency(line.amount)" class="pos-receipt-right-align"/>
                </div>

                <div  t-if="props.data.change != 0" class="pos-receipt-amount receipt-change">
                    CHANGE
                    <span t-esc="props.formatCurrency(props.data.change)" class="pos-receipt-right-align"/>
                </div>

                <!-- Extra Payment Info -->

                <t t-if="props.data.total_discount">
                    <div class="text-center">
                        Discounts
                        <span t-esc="props.formatCurrency(props.data.total_discount)" class="pos-receipt-right-align"/>
                    </div>
                </t>

                <div class="before-footer" />

                <div t-if="props.data.pos_qr_code">
                    <br/>
                    <div class="pos-receipt-order-data mb-2">
                        Need an invoice for your purchase ?
                    </div>
                </div>

                <div t-if="['qr_code', 'qr_code_and_url'].includes(props.data.headerData.company.point_of_sale_ticket_portal_url_display_mode) and props.data.pos_qr_code" class="mb-2">
                    <img id="posqrcode" t-att-src="props.data.pos_qr_code" class="pos-receipt-logo"/>
                </div>

                <div t-if="props.data.pos_qr_code">
                    <div class="pos-receipt-order-data">
                        Unique Code: <t t-esc="props.data.ticket_code"/>
                    </div>
                </div>

                <div t-if="['url', 'qr_code_and_url'].includes(props.data.headerData.company.point_of_sale_ticket_portal_url_display_mode) and props.data.pos_qr_code">
                    <div class="pos-receipt-order-data" t-attf-class="{{ props.data.ticket_portal_url_display_mode === 'qr_code_and_url' ? 'mt-3' : '' }}">
                        Portal URL: <t t-out="props.data.base_url"/>/pos/ticket
                    </div>
                </div>
            </t>

            <!-- Footer -->
           <div t-if="props.data.footer"  class="pos-receipt-center-align" style="white-space:pre-line">
               <br/>
               <t t-esc="props.data.footer" />
                <br/>
                <br/>
            </div>

            <div class="after-footer">
                <t t-foreach="props.data.paymentlines" t-as="line" t-key="line_index">
                    <t t-if="line.ticket">
                        <br />
                        <div class="pos-payment-terminal-receipt">
                            <pre t-esc="line.ticket" />
                        </div>
                    </t>
                </t>
            </div>

            <br/>
            <t t-if="props.data.shippingDate">
                <div class="pos-receipt-order-data">
                    Expected delivery:
                    <div><t t-esc="props.data.shippingDate" /></div>
                </div>
            </t>

            <br/>
            <div class="pos-receipt-order-data">
                <p>Powered by Odoo</p>
                <div t-esc="props.data.name" />
                <div id="order-date" t-esc="props.data.date" />
            </div>

        </div>"""
        self.create(record_data)

    @api.model
    def _create_order_receipt_design_2(self):
        record_data = {}
        record_data['name'] = "Order Receipt Design 2"
        record_data['company_id'] = self.env.company.id
        record_data['receipt_type'] = 'order'
        record_data['receipt_design_text'] = """
            <div class="pos-receipt p-2">
                <t t-set="showTaxGroupLabels" t-value="doesAnyOrderlineHaveTaxLabel()"/>
                <ReceiptHeader data="props.data.headerData" />
                <OrderWidget t-if="props.data.orderlines?.length" lines="props.data.orderlines" t-slot-scope="scope" generalNote="props.data.generalNote or ''" screenName="props.data.screenName">
                    <t t-set="line" t-value="scope.line"/>
                    <Orderline basic_receipt="props.basic_receipt" line="omit(scope.line, 'customerNote')" class="{ 'px-0': true }" showTaxGroupLabels="showTaxGroupLabels">
                        <li t-if="line.customerNote" class="customer-note w-100 p-2 my-1 rounded text-break">
                            <i class="fa fa-sticky-note me-1" role="img" aria-label="Customer Note" title="Customer Note"/>
                            <t t-esc="line.customerNote" />
                        </li>
                    </Orderline>
                </OrderWidget>
                <t t-if="!props.basic_receipt">
                    <div t-if="props.data.tax_details.length > 0" class="pos-receipt-taxes">
                        <div class="text-center">-------Order Receipt Design 2-------</div>
                        <div class="d-flex">
                            <span t-if="showTaxGroupLabels" class="me-2" style="visibility: hidden;">A</span>
                            <span class="fw-bolder">Untaxed Amount</span>
                            <span t-esc="props.formatCurrency(props.data.total_without_tax)" class="ms-auto"/>
                        </div>

                        <div t-foreach="props.data.tax_details" t-as="tax" t-key="tax.id" class="d-flex">
                            <t t-if="showTaxGroupLabels">
                                <span t-if="tax.tax_group_id.pos_receipt_label" t-esc="tax.tax_group_id.pos_receipt_label" class="me-2"/>
                                <span t-else="" class="me-2" style="visibility: hidden;">A</span>
                            </t>
                            <span>
                                <span t-esc="tax.name"/>
                                on
                                <span t-esc="props.formatCurrency(tax.base)"/>
                            </span>
                            <span t-esc="props.formatCurrency(tax.amount)" class="ms-auto"/>
                        </div>
                    </div>

                    <!-- Total -->
                    <div class="text-center">-------Order Receipt Design 2------</div>
                    <div class="pos-receipt-amount">
                        TOTAL
                        <span t-esc="props.formatCurrency(props.data.amount_total)" class="pos-receipt-right-align"/>
                    </div>
                    <t t-if="props.data.rounding_applied">
                        <div class="pos-receipt-amount">
                        Rounding
                        <span t-esc='props.formatCurrency(props.data.rounding_applied)' class="pos-receipt-right-align"/>
                        </div>
                        <div class="pos-receipt-amount">
                        To Pay
                        <span t-esc='props.formatCurrency(props.data.amount_total + props.data.rounding_applied)' class="pos-receipt-right-align"/>
                    </div>
                    </t>

                    <!-- Payment Lines -->

                    <div class="paymentlines text-start" t-foreach="props.data.paymentlines" t-as="line" t-key="line_index">
                        <t t-esc="line.name" />
                        <span t-esc="props.formatCurrency(line.amount)" class="pos-receipt-right-align"/>
                    </div>

                    <div  t-if="props.data.change != 0" class="pos-receipt-amount receipt-change">
                        CHANGE
                        <span t-esc="props.formatCurrency(props.data.change)" class="pos-receipt-right-align"/>
                    </div>

                    <!-- Extra Payment Info -->

                    <t t-if="props.data.total_discount">
                        <div class="text-center">
                            Discounts
                            <span t-esc="props.formatCurrency(props.data.total_discount)" class="pos-receipt-right-align"/>
                        </div>
                    </t>

                    <div class="before-footer" />

                    <div t-if="props.data.pos_qr_code">
                        <br/>
                        <div class="pos-receipt-order-data mb-2">
                            Need an invoice for your purchase ?
                        </div>
                    </div>

                    <div t-if="['qr_code', 'qr_code_and_url'].includes(props.data.headerData.company.point_of_sale_ticket_portal_url_display_mode) and props.data.pos_qr_code" class="mb-2">
                        <img id="posqrcode" t-att-src="props.data.pos_qr_code" class="pos-receipt-logo"/>
                    </div>

                    <div t-if="props.data.pos_qr_code">
                        <div class="pos-receipt-order-data">
                            Unique Code: <t t-esc="props.data.ticket_code"/>
                        </div>
                    </div>

                    <div t-if="['url', 'qr_code_and_url'].includes(props.data.headerData.company.point_of_sale_ticket_portal_url_display_mode) and props.data.pos_qr_code">
                        <div class="pos-receipt-order-data" t-attf-class="{{ props.data.ticket_portal_url_display_mode === 'qr_code_and_url' ? 'mt-3' : '' }}">
                            Portal URL: <t t-out="props.data.base_url"/>/pos/ticket
                        </div>
                    </div>
                </t>

                <!-- Footer -->
               <div t-if="props.data.footer"  class="pos-receipt-center-align" style="white-space:pre-line">
                   <br/>
                   <t t-esc="props.data.footer" />
                    <br/>
                    <br/>
                </div>

                <div class="after-footer">
                    <t t-foreach="props.data.paymentlines" t-as="line" t-key="line_index">
                        <t t-if="line.ticket">
                            <br />
                            <div class="pos-payment-terminal-receipt">
                                <pre t-esc="line.ticket" />
                            </div>
                        </t>
                    </t>
                </div>

                <br/>
                <t t-if="props.data.shippingDate">
                    <div class="pos-receipt-order-data">
                        Expected delivery:
                        <div><t t-esc="props.data.shippingDate" /></div>
                    </div>
                </t>

                <br/>
                <div class="pos-receipt-order-data">
                    <p>Powered by Odoo</p>
                    <div t-esc="props.data.name" />
                    <div id="order-date" t-esc="props.data.date" />
                </div>

            </div>"""
        self.create(record_data)

    @api.model
    def _create_bar_rest_receipt_design_1(self):
        record_data = {}
        record_data['name'] = "Res/Bar Receipt Design 1"
        record_data['company_id'] = self.env.company.id
        record_data['receipt_type'] = 'res_bar'
        record_data['receipt_design_text'] = """
                <div class="pos-receipt m-0 p-0">
            <!-- Receipt Header -->
            <div class="receipt-header text-center">
                <div class="pos-receipt-title">
                    <t t-if="changes.diningModeUpdate">
                        <t t-if="changes.takeaway">Dine In -&gt; Take Out</t>
                        <t t-else="">Take Out -&gt; Dine In</t>
                    </t>
                    <t t-else="">
                        <t t-if="changes.takeaway">Take Out</t>
                        <t t-else="">Dine In</t>
                    </t>
                </div>
                <div class="fs-2">
                    <span><t t-esc="changes.config_name"/> : <t t-esc="changes.time"/></span><br/>
                    <span>By: <t t-esc="changes.employee_name"/></span>
                </div>
                <span class="my-4" style="font-size: 120%;">
                    <t t-if="changes.table_name">Table <strong><t t-esc="changes.table_name"/></strong></t>
                    <t t-if="changes.tracking_number" class="fw-light my-3"> # <strong><t t-esc="changes.tracking_number"/></strong></t>
                </span>
            </div>
            <div class="text-center lh-1">-------------Res/Bar Receipt Design 1---------------</div>

            <!-- Receipt Body -->
            <div class="pos-receipt-body mb-4">
                <!-- Operational Title -->
                <t t-if="operational_title">
                    <div class="pos-receipt-title text-center" t-esc="operational_title" />
                </t>
                <!-- Order Lines -->
                <div t-foreach="changedlines" t-as="line" t-key="change_index">
                    <div t-attf-class="orderline #{line.isCombo ? 'mx-5 px-2' : 'mx-1'}">
                        <div class="d-flex medium">
                            <span class="me-3" t-esc="line.quantity"/> <span class="product-name" t-esc="line.basic_name"/>
                        </div>
                        <div t-if="line.attribute_value_ids?.length" class="mx-5 fs-2">
                            <t t-foreach="line.attribute_value_ids" t-as="attribute" t-key="attribute.id">
                                <p class="p-0 m-0">
                                    - <t t-esc="attribute.name" /><br/>
                                </p>
                            </t>
                        </div>
                        <div t-if="line.note" class="fs-2 fst-italic">
                            <t t-esc="line.note.split('\n').join(', ')"/><br/>
                        </div>
                        <div t-if="line.sticker_note" class="fs-2 fst-italic">
                            <t t-esc="line.sticker_note.split('\n').join(', ')"/><br/>
                        </div>
                    </div>
                </div>
                <!-- General Note -->
                <!-- if no orderline change that means general note change to handle with less arguments -->
                <t t-if="(!changedlines.length or fullReceipt) and changes.order_note.length">
                    <div class="fs-2 my-5 fst-italic">
                        <t t-if="changes.order_note">
                            <t t-esc="changes.order_note.split('\n').join(', ')"/><br/>
                        </t>
                    </div>
                </t>
            </div>
        </div>"""
        self.create(record_data)

    @api.model
    def _create_bar_rest_receipt_design_2(self):
        record_data = {}
        record_data['name'] = "Res/Bar Receipt Design 2"
        record_data['company_id'] = self.env.company.id
        record_data['receipt_type'] = 'res_bar'
        record_data['receipt_design_text'] = """
            <div class="pos-receipt m-0 p-0">
                <!-- Receipt Header -->
                <div class="receipt-header text-center">
                    <div class="pos-receipt-title">
                        <t t-if="changes.diningModeUpdate">
                            <t t-if="changes.takeaway">Dine In -&gt; Take Out</t>
                            <t t-else="">Take Out -&gt; Dine In</t>
                        </t>
                        <t t-else="">
                            <t t-if="changes.takeaway">Take Out</t>
                            <t t-else="">Dine In</t>
                        </t>
                    </div>
                    <div class="fs-2">
                        <span><t t-esc="changes.config_name"/> : <t t-esc="changes.time"/></span><br/>
                        <span>By: <t t-esc="changes.employee_name"/></span>
                    </div>
                    <span class="my-4" style="font-size: 120%;">
                        <t t-if="changes.table_name">Table <strong><t t-esc="changes.table_name"/></strong></t>
                        <t t-if="changes.tracking_number" class="fw-light my-3"> # <strong><t t-esc="changes.tracking_number"/></strong></t>
                    </span>
                </div>
                <div class="text-center lh-1">-------------Res/Bar Receipt Design 2---------------</div>

                <!-- Receipt Body -->
                <div class="pos-receipt-body mb-4">
                    <!-- Operational Title -->
                    <t t-if="operational_title">
                        <div class="pos-receipt-title text-center" t-esc="operational_title" />
                    </t>
                    <!-- Order Lines -->
                    <div t-foreach="changedlines" t-as="line" t-key="change_index">
                        <div t-attf-class="orderline #{line.isCombo ? 'mx-5 px-2' : 'mx-1'}">
                            <div class="d-flex medium">
                                <span class="me-3" t-esc="line.quantity"/> <span class="product-name" t-esc="line.basic_name"/>
                            </div>
                            <div t-if="line.attribute_value_ids?.length" class="mx-5 fs-2">
                                <t t-foreach="line.attribute_value_ids" t-as="attribute" t-key="attribute.id">
                                    <p class="p-0 m-0">
                                        - <t t-esc="attribute.name" /><br/>
                                    </p>
                                </t>
                            </div>
                            <div t-if="line.note" class="fs-2 fst-italic">
                                <t t-esc="line.note.split('\n').join(', ')"/><br/>
                            </div>
                            <div t-if="line.sticker_note" class="fs-2 fst-italic">
                                <t t-esc="line.sticker_note.split('\n').join(', ')"/><br/>
                            </div>
                        </div>
                    </div>
                    <!-- General Note -->
                    <!-- if no orderline change that means general note change to handle with less arguments -->
                    <t t-if="(!changedlines.length or fullReceipt) and changes.order_note.length">
                        <div class="fs-2 my-5 fst-italic">
                            <t t-if="changes.order_note">
                                <t t-esc="changes.order_note.split('\n').join(', ')"/><br/>
                            </t>
                        </div>
                    </t>
                </div>
            </div>"""
        self.create(record_data)

