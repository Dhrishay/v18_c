/* @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { NumberOfGuest } from "@lo_pos_guest_info/number_of_guest_popup/number_of_guest";
import { makeAwaitable, ask } from "@point_of_sale/app/store/make_awaitable_dialog";
import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";
import { useService } from "@web/core/utils/hooks";

patch(ActionpadWidget.prototype, {
    setup() {
        super.setup();
        this.dialog = useService("dialog");
    },

    async submitOrder() {
        const order = this.currentOrder
        if (this.pos.config.is_guest_details && this.pos.config.guest_details_timing == 'after' && order && order.id !== "number"){
            const resp = await makeAwaitable(this.dialog, NumberOfGuest, {table_order: order});
            if (resp){
                for (const guest in resp){
                    if (resp[guest].age && resp[guest].nationality && resp[guest].gender){
                        const values = {
                                    age: resp[guest].age,
                                    country_id: this.pos.data.records['res.country'].get(parseInt(resp[guest].nationality)),
                                    gender: resp[guest].gender,
                                    company_id: this.pos.company,
                                    config_id: this.pos.config,
                                    session_id: this.pos.session,
                                    user_id: this.pos.get_cashier(),
                                }
                    const line = this.pos.data.models["guest.detail"].create({ ...values});
                    order.guest_detail_ids.push(line)
//                    order.customer_count = order.guest_detail_ids.length
//                    const genderCount = order.guest_detail_ids.reduce((acc, guest) => {
//                        if (guest.gender) {
//                            acc[guest.gender] = (acc[guest.gender] || 0) + 1;
//                        }
//                        return acc;
//                    }, {});
//                    order.no_of_male = genderCount.male || 0
//                    order.no_of_female = genderCount.female || 0
                    }
                }
                await super.submitOrder(...arguments);
            }
        }
        else{
            await super.submitOrder(...arguments);
        }
    },
});


patch(ProductScreen.prototype, {

    async submitOrder() {
        const order = this.currentOrder
        if (this.pos.config.is_guest_details && this.pos.config.guest_details_timing == 'after' && order && order.id !== "number"){
            const resp = await makeAwaitable(this.dialog, NumberOfGuest, {table_order: order});
            if (resp){
                for (const guest in resp){
                    if (resp[guest].age && resp[guest].nationality && resp[guest].gender){
                        const values = {
                                    age: resp[guest].age,
                                    country_id: this.pos.data.records['res.country'].get(parseInt(resp[guest].nationality)),
                                    gender: resp[guest].gender,
                                    company_id: this.pos.company,
                                    config_id: this.pos.config,
                                    session_id: this.pos.session,
                                    user_id: this.pos.get_cashier(),
                                }
                    const line = this.pos.data.models["guest.detail"].create({ ...values});
                    order.guest_detail_ids.push(line)
//                    order.customer_count = order.guest_detail_ids.length
//                    const genderCount = order.guest_detail_ids.reduce((acc, guest) => {
//                        if (guest.gender) {
//                            acc[guest.gender] = (acc[guest.gender] || 0) + 1;
//                        }
//                        return acc;
//                    }, {});
//                    order.no_of_male = genderCount.male || 0
//                    order.no_of_female = genderCount.female || 0
                    }
                }
                await super.submitOrder(...arguments);
            }
        }
        else{
            await super.submitOrder(...arguments);
        }
    },
});
