/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { SelectCreateDialog } from "@web/views/view_dialogs/select_create_dialog";
import { makeAwaitable, ask } from "@point_of_sale/app/store/make_awaitable_dialog";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { NumberOfGuest } from "@lo_pos_guest_info/number_of_guest_popup/number_of_guest";


patch(ControlButtons.prototype, {
    async ShowGuestPopup() {
        const order = this.pos.get_order();
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
//                order.customer_count = order.guest_detail_ids.length
//                const genderCount = order.guest_detail_ids.reduce((acc, guest) => {
//                        if (guest.gender) {
//                            acc[guest.gender] = (acc[guest.gender] || 0) + 1;
//                        }
//                        return acc;
//                    }, {});
//                order.no_of_male = genderCount.male || 0
//                order.no_of_female = genderCount.female || 0
                }
            }
        }
    },
});
