/* @odoo-module */

import { BasePrinter } from "@point_of_sale/app/printer/base_printer";
import { _t } from "@web/core/l10n/translation";
import { htmlToCanvas } from "@point_of_sale/app/printer/render_service";


/**
 * Sends print request to printer that is directly connected to the local network.
 */
export class EscPosPrinter extends BasePrinter {
    setup({ ip, order_receipt_type, port, receipt_design, receipt_design_text, sticker_printer, escpos_print_cashdrawer,receipt }) {
        super.setup(...arguments);
        this.url = "/lo_pos_tcp_escpos_printer/print";
        this.ip = ip;
        this.order_receipt_type = order_receipt_type || 'all';
        this.port = port;
        this.receipt_design = receipt_design;
        this.receipt_design_text = receipt_design_text
        this.sticker_printer = sticker_printer
        this.escpos_print_cashdrawer = escpos_print_cashdrawer
    }

    /**
     * @override
     */
    async sendPrintingJob(img) {
        const res = await fetch(this.url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },

            body: JSON.stringify({
                img: this.sticker_printer ? [] : img,
                ip: this.ip,
                order_receipt_type: this.order_receipt_type,
                port: this.port,
                receipt_design: this.receipt_design,
                receipt_design_text: this.receipt_design_text,
                sticker_printer: this.sticker_printer,
                sticker_data: this.sticker_printer ? img : [],
                escpos_print_cashdrawer: this.escpos_print_cashdrawer
            })
        });
        const body = await res.json();
        return {
            result: true,
            printerErrorCode: 0,
        };
    }
}