import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { useBus } from "@web/core/utils/hooks";
import { ask } from "@point_of_sale/app/store/make_awaitable_dialog";
import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";

patch(PaymentScreen.prototype, {
        setup() {
            super.setup(...arguments);
            useBus(this.env.bus, 'validate-order', () => this.validate_order());
        },
        async validate_order(){
            this.validateOrder(true);
        },
        async addNewPaymentLine(paymentMethod) {
            var self = this ;
            var qr_code = ''
            if (paymentMethod.is_iblaos_payment){
                if (!this.currentOrder.get_partner()) {
                    const confirmed = await ask(this.dialog, {
                        title: _t("Customer Required"),
                        body: _t("Customer is required for %s payment method.", paymentMethod.name),
                    });
                    if (confirmed) {
                        this.pos.selectPartner();
                    }
                    return false;
                }else{
                    var order = this.currentOrder
                    var amount = this.currentOrder.get_due()
                    var result_qr = await rpc('/web/dataset/call_kw', {
                        model: 'pos.order', method: 'get_kok_ib_qr_code',
                        args: [
                            [], order.id, amount, this.pos.config.id, this.pos.session.id
                        ],
                        kwargs: {},
                    });
                    qr_code = "data:image/png;base64,"+result_qr;
                    if (this.pos.config.customer_display_type !== "none"){
                        order.qr_code = qr_code
                    }
                }
            }
            return await super.addNewPaymentLine(...arguments);
        },
//
        get nextScreen() {
            var order = this.currentOrder
            if (!this.error){
                order.qr_code = ''
            }
            return super.nextScreen;
        },

        deletePaymentLine(uuid) {
            const line = this.paymentLines.find((line) => line.uuid === uuid);
            var order = this.currentOrder
            if (line.payment_method_id.is_iblaos_payment && this.pos.config.customer_display_type !== "none"){
                    order.qr_code = ''
                    if(document.getElementsByClassName('next_text')[0] && document.getElementsByClassName('next_text')[0].parentNode){
                        document.getElementsByClassName('next_text')[0].parentNode.classList.add('disabled')
                    }
            }
            if (line.payment_method_id.payment_method_type === "qr_code") {
                this.currentOrder.remove_paymentline(line);
                this.numberBuffer.reset();
                return;
            }
            // If a paymentline with a payment terminal linked to
            // it is removed, the terminal should get a cancel
            // request.
            if (["waiting", "waitingCard", "timeout"].includes(line.get_payment_status())) {
                line.set_payment_status("waitingCancel");
                line.payment_method_id.payment_terminal
                    .send_payment_cancel(this.currentOrder, uuid)
                    .then(() => {
                        this.currentOrder.remove_paymentline(line);
                        this.numberBuffer.reset();
                    });
            } else if (line.get_payment_status() !== "waitingCancel") {
                this.currentOrder.remove_paymentline(line);
                this.numberBuffer.reset();
            }
        },

        async ToggleIsToPaymentRef() {
                var order = this.currentOrder
//                const payment_kokkok = this.paymentLines.find((line) => line.payment_method.is_kok_payment)

                const { confirmed, payload: inputNote } = this.dialog.add(TextInputPopup, {
                    title: _t("Payment Ref"),
                    placeholder: _t(""),
                    getPayload: async (code) => {
                        code = code.trim();
                    },
                });

//                var cash_back_amount = 0;
//                var lines = order.get_orderlines();
//                var client =  this.currentOrder.get_partner()
//                var category_ids = ''
//                console.log("++this.env.pos.cash_back_config",this.env.pos.cash_back_config)
//                if (client){
//                    _.each(this.env.pos.cash_back_config, function (cash_back) {
//                        category_ids = cash_back.exc_product_categ_ids
//                    });
//                }
//                lines.map(function(line){
//                    if (category_ids.indexOf(line.product.categ_id[0]) == -1){
//                        cash_back_amount += line.get_display_price() * line.quantity
//                    }
//                });
//
//
//                var cash_amount = 0;


//                if (cash_back_amount > 0 && client && payment_kokkok){
//                    _.each(this.env.pos.cash_back_config, function (cash_back) {
//                        if (cash_back.from_amount <= cash_back_amount &&
//                            cash_back_amount <= cash_back.to_amount &&
//                            client.membership_level == cash_back.membership_level){
//                            cash_amount = (cash_back.percentage * cash_back_amount) / 100
//                        }
//                    });
//                }

                if (confirmed){
                    order.kok_payment_ref = inputNote
                    this.validateOrder(true);
                }
            },

        async updateSelectedPaymentline(amount = false) {
            super.updateSelectedPaymentline()
             if (this.selectedPaymentLine != undefined && this.selectedPaymentLine.amount > 0 && this.selectedPaymentLine.payment_method_id.is_iblaos_payment) {
                var order = this.currentOrder
                var amount = this.selectedPaymentLine.amount
                var config_id = this.pos.config.id

                var qr_code = ''
                var result_qr = await rpc('/web/dataset/call_kw', {
                    model: 'pos.order', method: 'get_kok_ib_qr_code',
                    args: [[], order.id, amount, this.pos.config.id, this.pos.session.id],
                    kwargs: {},
                });
                qr_code = "data:image/png;base64,"+result_qr;
                if (this.pos.config.customer_display_type !== "none"){
                    order.qr_code = qr_code

                }
            }

        }

});
