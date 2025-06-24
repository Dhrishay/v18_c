/** @odoo-module */

import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { _t } from "@web/core/l10n/translation";

patch(PosStore.prototype, {
    async pay() {
        const currentOrder = this.get_order();

        if (!currentOrder.canPay()) {
            return;
        }
        for(let line of currentOrder.lines){
            if(!line.is_reward_line && !line.refunded_orderline_id && (line.qty <= 0 || line.price_unit <= 0.00) ){
                this.dialog.add(AlertDialog, {
                    title: _t("Alert"),
                    body: _t("Order cannot be processed with zero (0) quantity or zero total price."),
                });
                return;
            }
        }

        if (
            currentOrder.lines.some(
                (line) => line.get_product().tracking !== "none" && !line.has_valid_product_lot()
            ) &&
            (this.pickingType.use_create_lots || this.pickingType.use_existing_lots)
        ) {
            const confirmed = await ask(this.env.services.dialog, {
                title: _t("Some Serial/Lot Numbers are missing"),
                body: _t(
                    "You are trying to sell products with serial/lot numbers, but some of them are not set.\nWould you like to proceed anyway?"
                ),
            });
            if (confirmed) {
                this.mobile_pane = "right";
                this.env.services.pos.showScreen("PaymentScreen", {
                    orderUuid: this.selectedOrderUuid,
                });
            }
        } else {
            this.mobile_pane = "right";
            this.env.services.pos.showScreen("PaymentScreen", {
                orderUuid: this.selectedOrderUuid,
            });
        }
    }
});
