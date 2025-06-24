import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { _t } from "@web/core/l10n/translation";

patch(PosStore.prototype, {
    /**
     * @override
     */
    async setup() {
        await super.setup(...arguments);
        this.bus.subscribe("iblaos_qr_callback", (payload) => {
            const order = this.get_order()
            if (payload.data && order != undefined){
                var order_amount = order ? order.get_total_with_tax() : 0;
                var order_name = payload.data.order_name;
                var session_name = payload.data.session_name;
                const paymentLine = order.get_selected_paymentline();
                if (paymentLine){
                    paymentLine.payment_ref_no = payload.data.pay_ref
                }
                if (order && order.id.toString() == order_name && this.session.name == session_name){
                    order.qr_code = ''
                    this.env.bus.trigger("validate-order");
                }
          }
        });

    },

});
