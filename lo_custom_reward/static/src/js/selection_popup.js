import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { roundPrecision as round_pr } from "@web/core/utils/numbers";

patch(SelectionPopup.prototype, {
    setup() {
        super.setup(...arguments);
         this.pos = usePos();
    },
    async selectItem(itemId) {
        var tmp = false
        this.props.list.forEach((reward, index) => {
            if (reward.id == itemId && reward.name == "qr_code_name") {
                tmp = true
            }
        });
        if (tmp){
            var total_points = this.pos.get_order()?.getLoyaltyPoints()
                const sum = total_points.reduce(
                    (acc, item) => {
                        if (item.points){
                            acc.total += item.points.total || 0; // Add total
                            acc.spent += item.points.spent || 0; // Add spent
                            acc.won += item.points.won || 0; // Add spent
                            return acc;
                        }
                    },
                    { total: 0, spent: 0, won: 0 } // Initial value for sums
                );

                var member_id = this.pos.get_order()?.get_partner().id
                var cashier_id = this.pos.get_cashier().id
                var point_bill = round_pr(sum.spent, this.pos.currency.rounding);
                var total_score = round_pr(sum.total, this.pos.currency.rounding)
                var amount_bill = this.pos.get_order() ? this.pos.get_order().get_total_with_tax() : 0;
                var tem_bill_id = Math.floor((Math.random() * Number(member_id)*Math.random() * 100000));

                if (! this.pos.config.use_incoming_points){
                    var total_score = round_pr(sum.total - sum.won, this.pos.currency.rounding)
                }

                var data = {
                    "result": "Yes",
                    "reward_type": "point",
                    "member_id": member_id,
                    "cashier_id": cashier_id,
                    "session_id": this.pos.session.id,
                    "current_order": this.pos.get_order().pos_reference,
                    "bill_id": tem_bill_id,
                    "point_bill": point_bill,
                    "bill_amount": amount_bill,
                    "loy_type": 1,
                    "base_point": 1,
                    "base_amount": 1,
                    "total_point": total_score,
                    "loyalty_point": 0
                }
                const res = await this.pos.data.call("pos.order", "get_qr_code", [ data]);
                var order = this.pos.get_order()
                if (res){
                    var qr_code = "data:image/png;base64,"+res;
                    if (this.pos.config.customer_display_type){
                        order.qr_code = qr_code
                        order.qr_reward_id = itemId
                        const customerDisplayData = order.getCustomerDisplayData();
                        customerDisplayData.qr_code = qr_code
                        this.props.close();
                        return
                    }
                }
        }
        this.state.selectedId = itemId;
        this.confirm();
    }
});