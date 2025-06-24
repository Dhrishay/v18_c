import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { Component, useState, xml } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { PopupLocationWidget } from "@bi_pos_reports/js/AuditReport/PopupLocationWidget";
import { PopupCategoryWidget } from "@bi_pos_reports/js/CategorySummary/PopupCategoryWidget";
import { PopupOrderWidget } from "@bi_pos_reports/js/OrderSummary/PopupOrderWidget";
import { PopupPaymentWidget } from "@bi_pos_reports/js/PaymentReport/PaymentSummaryPopup";
import { PopupProductWidget } from "@bi_pos_reports/js/ReportProductButton/PopupProductWidget";


patch(ControlButtons.prototype, {

    setup() {
        super.setup();
        this.orm = useService("orm");
        
    },

    clickReports(){
        this.dialog.add(ReportsButtonsPopup,{});
    }

});

export class ReportsButton extends Component {
    static template = "bi_pos_reports.ReportsButton";
    // static props = ["close"]

    setup() {
        super.setup();
        this.dialog = useService("dialog");
        this.pos = usePos();
    }

    async clickAuditReport(){
        let sessions = await this.env.services.orm.call('pos.session','search_read', [[]]);
        this.dialog.add(PopupLocationWidget,{sessions: sessions});
    }

    clickCategorySummary(){
        this.dialog.add(PopupCategoryWidget,{});
    }

    clickProductSummary(){
        this.dialog.add(PopupProductWidget,{});
    }

    clickOrderSummary(){
        this.dialog.add(PopupOrderWidget,{});
    }

    clickPaymentSummary(){
        this.dialog.add(PopupPaymentWidget,{});
    }
}

export class ReportsButtonsPopup extends Component {
    static components = { Dialog, ReportsButton };
    static template = xml`
        <Dialog bodyClass="'d-flex flex-column'" footer="false" title="'Reports'" t-on-click="props.close">
            <ReportsButton/>
        </Dialog>
    `;
    static props = {
        close: Function,
    };
}
