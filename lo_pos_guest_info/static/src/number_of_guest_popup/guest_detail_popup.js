/* @odoo-module */

import { Dialog } from "@web/core/dialog/dialog";
import { Component, useState, xml } from "@odoo/owl";
import { makeAwaitable, ask } from "@point_of_sale/app/store/make_awaitable_dialog";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";


export class GuestDetail extends Component {
    static components = { Dialog };
    static props = {
        close: Function,
        getPayload: { type: Function },
        total_guest: { type: Array, optional: false },
        current_order: { type: Object, optional: false },
    };

    async setup() {
        super.setup();
        this.pos = usePos();
        this.dialog = useService("dialog");
    }

    async confirm(ev) {
    // Locate the dialog container from the button event
        const dialogElement = ev.currentTarget.closest('.modal-dialog');

        if (dialogElement) {
            // Select all inputs
            const inputs = dialogElement.querySelectorAll('input, select');
            const guests = {};

            inputs.forEach(input => {
                const name = input.getAttribute('name');
                if (name) {
                    // Extract the prefix (e.g., "name_", "age_", etc.)
                    const [key, count] = name.split('_');
                    if (!guests[count]) {
                        guests[count] = {};
                    }
                    guests[count][key] = input.value;
                }
            });
            var stop_process = false;
            if (guests) {
                Object.entries(guests).forEach(([key, value]) => {
                    if (!value.age || !value.nationality || !value.gender) {
                        stop_process = true;
                    }
                });
            }

            if (!stop_process && guests){
                this.props.getPayload(guests);
                this.props.close();
            }
            else if (this.pos.config.guest_details_required) {
                ask(this.dialog, {
                    title: _t("Invalid Details"),
                    body: _t("Please fill all the details properly."),
                });
            }
            else {
                this.props.getPayload(guests);
                this.props.close();
            }

        } else {
            console.error('Dialog element not found!');
        }
    }

    async skip() {
        this.props.getPayload({skip: true});
        this.props.close();
    }

    static template = xml`
        <Dialog title="'Guest Detail'" >
            <t class="'body'">
                <t t-foreach="props.total_guest" t-as="count" t-key="count">
                    <div class="mt-3" ><h3>Customer-<t t-esc="count"/></h3>
                        <t t-if="this.props.current_order.guest_detail_ids[count-1]">
                            <div class="row">
                            <div class="col-md-2  mt-3 o_colored_level">
                                <label for="age" class="o_default_snippet_text">Age: </label>
                            </div>
                            <div class="col-md-2  mt-3 o_colored_level">
                                <input class="form-control" style="border-color: #838383;"
                                    t-att-value="this.props.current_order.guest_detail_ids[count-1].age" type="number" readonly="readonly"/>
                            </div>

                            <div class="col-md-2  mt-3 o_colored_level">
                                <label for="nationality" class="o_default_snippet_text">Nationality: </label>
                            </div>
                            <div class="col-md-2  mt-3 o_colored_level">
                                <input class="form-control" style="border-color: #838383;"
                                    t-att-value="this.props.current_order.guest_detail_ids[count-1].country_id.name" readonly="readonly"/>
                            </div>

                            <div class="col-md-2  mt-3 o_colored_level">
                                <label t-att-for="gender" class="o_default_snippet_text">Gender: </label>
                            </div>
                            <div class="col-md-2  mt-3 o_colored_level">
                                <input class="form-control" style="border-color: #838383;"
                                    t-att-value="this.props.current_order.guest_detail_ids[count-1].gender" readonly="readonly"/>
                            </div>
                        </div>
                        </t>
                        <t t-else="">
                            <div class="row">
                                <div class="col-md-2  mt-3 o_colored_level">
                                    <label t-att-for="'age_' + count" class="o_default_snippet_text">Age: </label>
                                </div>
                                <div class="col-md-2  mt-3 o_colored_level">
                                    <input class="form-control" style="border-color: #838383;" t-att-name="'age_' + count" type="number"/>
                                </div>

                                <div class="col-md-2  mt-3 o_colored_level">
                                    <label t-att-for="'nationality_' + count" class="o_default_snippet_text">Nationality: </label>
                                </div>
                                <div class="col-md-2  mt-3 o_colored_level">
                                    <select class="form-control" style="border-color: #838383;" t-att-name="'nationality_' + count">
                                        <t t-foreach="this.pos.data.records['res.country']" t-as="country" t-key="country">
                                             <option t-att-selected="this.pos.data.records['res.country'].get(country).id === this.pos.company.country_id.id"
                                                t-att-value="this.pos.data.records['res.country'].get(country).id">
                                                <t t-esc="this.pos.data.records['res.country'].get(country).name"/>
                                             </option>
                                        </t>
                                    </select>
                                </div>

                                <div class="col-md-2  mt-3 o_colored_level">
                                    <label t-att-for="'gender_'+ count" class="o_default_snippet_text">Gender: </label>
                                </div>
                                <div class="col-md-2  mt-3 o_colored_level">
                                    <select class="form-control" style="border-color: #838383;" t-att-name="'gender_'+ count">
                                        <option value=""/>
                                        <option value="male">Male</option>
                                        <option value="female">Female</option>
                                    </select>
                                </div>
                            </div>
                        </t>
                    </div>
                </t>
            </t>
            <t t-set-slot="footer">
                <div class="'modal-footer-left d-flex gap-2'">
                    <div class="'modal-footer-left d-flex gap-2'">
                        <button style="margin-right: 10px" class="button highlight btn btn-lg btn-primary" t-on-click="confirm">Next</button>
                        <button style="margin-right: 10px" class="button btn btn-lg btn-secondary" t-on-click="props.close">Previous</button>
                        <button class="button btn btn-lg btn-secondary" t-on-click="skip">Skip</button>
                    </div>
                </div>
            </t>
        </Dialog>
    `;

}
