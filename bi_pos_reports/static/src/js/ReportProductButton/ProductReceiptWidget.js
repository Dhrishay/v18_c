/** @odoo-module */

import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component, useRef } from "@odoo/owl";
import { XMLPosProductSummaryReceipt } from "@bi_pos_reports/js/ReportProductButton/XMLPosProductSummaryReceipt";
import { useService } from "@web/core/utils/hooks";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";

export class ProductReceiptWidget extends ReceiptScreen {
    static template = "bi_pos_reports.ProductReceiptWidget";
    static components = { XMLPosProductSummaryReceipt }
    static props = [
    	"output_summery_product", 
    	"pro_st_date", 
    	"pro_ed_date",
    	"prod_current_session"]

    setup() {
        super.setup(...arguments);
        this.pos = usePos();
        this.printer = useService("printer");
        this.buttonPrintReceipt = useRef("order-print-receipt-button");
    }

    back() {
        this.pos.closeScreen();
        this.pos.showScreen('ProductScreen');
    }

    async printReceipt() {
        this.buttonPrintReceipt.el.className = "fa fa-fw fa-spin fa-circle-o-notch";
        const isPrinted = await this.printer.print(
            XMLPosProductSummaryReceipt,
            {
                data: this.pos.get_order().export_for_printing(),
                formatCurrency: this.env.utils.formatCurrency,
                order: this.get_product_receipt_data(),
            },
            { webPrintFallback: true }
        );

        if (isPrinted) {
            this.currentOrder._printed = true;
        }

        if (this.buttonPrintReceipt.el) {
            this.buttonPrintReceipt.el.className = "fa fa-print";
        }
    }
    
    get_product_receipt_data(){
		return {
			widget: this,
			pos: this.pos,
			prod_current_session : this['props']['prod_current_session'],
			p_summery: this.get_pro_summery(),
			p_st_date: this.get_product_st_date(),
			p_ed_date: this.get_product_ed_date(),
			date_p: (new Date()).toLocaleString(),
			langs:this.pos.langs,
		};
		
	}

    get_pro_summery(){
		return this['props']['output_summery_product'];
	}

	get_product_st_date(){
		return this['props']['pro_st_date'];
	}
	get_product_ed_date(){
		return this['props']['pro_ed_date'];
	}

	get product_receipt_data() {
		return {
			widget: this,
			pos: this.pos,
			prod_current_session : this['props']['prod_current_session'],
			p_summery: this.get_pro_summery(),
			p_st_date: this.get_product_st_date(),
			p_ed_date: this.get_product_ed_date(),
			date_p: (new Date()).toLocaleString(),
			langs:this.pos.langs,
		};
	}

    
}

registry.category("pos_screens").add("ProductReceiptWidget", ProductReceiptWidget);

