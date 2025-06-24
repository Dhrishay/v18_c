/* @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { OnlinePaymentPopup } from "@pos_online_payment/app/online_payment_popup/online_payment_popup";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { qrCodeSrc } from "@point_of_sale/utils";
import { ask } from "@point_of_sale/app/store/make_awaitable_dialog";

patch(PaymentScreen.prototype, {
    async addNewPaymentLine(paymentMethod) {
        if (this.currentOrder.pay_later_order && !paymentMethod.is_pay_later){
            this.paymentLines.forEach((line) => {
                if (line.payment_method_id && line.payment_method_id.is_pay_later) {
                    this.deletePaymentLine(line.uuid);
                   this.currentOrder.remove_paymentline(line);
                }
            });
            await this.pos.syncAllOrders()
            this.currentOrder.pay_later_order =  false
        }

        if (paymentMethod.is_pay_later){
            if (!this.currentOrder.get_partner()) {
                const confirmed = await ask(this.dialog, {
                    title: _t("Please select the Customer"),
                    body: _t(
                        "You need to select the customer before you can invoice or ship an order."
                    ),
                });
                if (confirmed) {
                    this.pos.selectPartner();
                }
                return false;
            }
            await this.pos.syncAllOrders()
            this.currentOrder.pay_later_order =  true
        }
        return await super.addNewPaymentLine(...arguments);
    },

     async validateOrder(isForceValidate) {
         if (this.currentOrder.pay_later_order){
            this.env.services.ui.block();
            const res = await this.pos.data.call("pos.order", "set_pay_later_order", [[this.currentOrder.id]]);
            this.env.services.ui.unblock();
            this.pos.showScreen("ReceiptScreen");
            return
         }
        await super.validateOrder(...arguments);
    },
});
