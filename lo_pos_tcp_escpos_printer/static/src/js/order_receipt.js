/** @odoo-module */

import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { patch } from "@web/core/utils/patch"
import { useState, xml } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { PrinterService } from "@point_of_sale/app/printer/printer_service";
import { loadAllImages } from "@point_of_sale/utils";


patch(OrderReceipt.prototype, {
    setup() {
        super.setup();
        this.state = useState({
            template: true,
        })
        this.pos = useState(useService("pos"));
    },
    get CustomOrderReceipt() {
        var self = this
        return class extends OrderReceipt {
            static template = xml`${self.pos.config.receipt_design_text}`
        }
    },
    get isCustomeTemplate() {
        if (this.env.services.pos.config.receipt_design_text) {
            return false;
        } else {
            return true;
        }
    }
});

patch(PrinterService.prototype, {
    async print(component, props, options) {
        this.state.isPrinting = true;
        var el = await this.renderer.toHtml(component, props);
        if (typeof (el) === 'object') {
            var el = el.nextElementSibling;
        }
        try {
            await loadAllImages(el);
        } catch (e) {
            console.error("Images could not be loaded correctly", e);
        }
        try {
            return await this.printHtml(el, options);
        } finally {
            this.state.isPrinting = false;
        }
    }
});