/* @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { ConnectionLostError } from "@web/core/network/rpc";
import { NumberOfGuest } from "@lo_pos_guest_info/number_of_guest_popup/number_of_guest";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
//import { SERIALIZABLE_MODELS } from "@point_of_sale/app/models/related_models";

//SERIALIZABLE_MODELS.push("guest.detail")

patch(PosStore.prototype, {
    async setTableFromUi(table, orderUuid = null) {
        try {
            this.tableSyncing = true;
            if (table.parent_id) {
                table = table.getParent();
            }
            await this.setTable(table, orderUuid);
        } catch (e) {
            if (!(e instanceof ConnectionLostError)) {
                throw e;
            }
            // Reject error in a separate stack to display the offline popup, but continue the flow
            Promise.reject(e);
        } finally {
            this.tableSyncing = false;
            const orders = this.getTableOrders(table.id);
            if (this.config.is_guest_details && this.config.guest_details_timing == 'before' && orders && typeof orders[0].id !== "number"){
                const resp = await makeAwaitable(this.dialog, NumberOfGuest, {table_order: orders[0]});
                if (resp){
                    if (orders.length > 0) {
                        this.set_order(orders[0]);
                        const props = {};
                        if (orders[0].get_screen_data().name === "PaymentScreen") {
                            props.orderUuid = orders[0].uuid;
                        }
                        for (const guest in resp){
                            if (resp[guest].age && resp[guest].nationality && resp[guest].gender){
                                const values = {
                                            age: resp[guest].age,
                                            country_id: this.data.records['res.country'].get(parseInt(resp[guest].nationality)),
                                            gender: resp[guest].gender,
                                            company_id: this.company,
                                            config_id: this.config,
                                            session_id: this.session,
                                            user_id: this.get_cashier(),
                                        }
                            const line = this.data.models["guest.detail"].create({ ...values});
                            orders[0].guest_detail_ids.push(line)
//                            orders[0].customer_count = orders[0].guest_detail_ids.length
//                            const genderCount = orders[0].guest_detail_ids.reduce((acc, guest) => {
//                                if (guest.gender) {
//                                    acc[guest.gender] = (acc[guest.gender] || 0) + 1;
//                                }
//                                return acc;
//                            }, {});
//                            orders[0].no_of_male = genderCount.male || 0
//                            orders[0].no_of_female = genderCount.female || 0
                            }
                        }
                        this.showScreen(orders[0].get_screen_data().name, props);
                    }
                    else {
                        const order = this.add_new_order();
                        for (const guest in resp){
                            if (resp[guest].age && resp[guest].nationality && resp[guest].gender){
                                const values = {
                                            age: resp[guest].age,
                                            country_id: this.data.records['res.country'].get(parseInt(resp[guest].nationality)),
                                            gender: resp[guest].gender,
                                            company_id: this.company,
                                            config_id: this.config,
                                            session_id: this.session,
                                            user_id: this.get_cashier(),
                                        }
                            const line = this.data.models["guest.detail"].create({ ...values});
                            order.guest_detail_ids.push(line)
//                            order.customer_count = order.guest_detail_ids.length
//                            const genderCount = order.guest_detail_ids.reduce((acc, guest) => {
//                                if (guest.gender) {
//                                    acc[guest.gender] = (acc[guest.gender] || 0) + 1;
//                                }
//                                return acc;
//                            }, {});
//                            order.no_of_male = genderCount.male || 0
//                            order.no_of_female = genderCount.female || 0
                            }
                        }
                        this.showScreen("ProductScreen");
                    }
                }
            }
            else{
                if (orders.length > 0) {
                    this.set_order(orders[0]);
                    const props = {};
                    if (orders[0].get_screen_data().name === "PaymentScreen") {
                        props.orderUuid = orders[0].uuid;
                    }
                    this.showScreen(orders[0].get_screen_data().name, props);
                } else {
                    this.add_new_order();
                    this.showScreen("ProductScreen");
                }
            }
        }
    },
});
