/* @odoo-module */

import { Dialog } from "@web/core/dialog/dialog";
import { Component, useState, xml } from "@odoo/owl";
import { makeAwaitable, ask } from "@point_of_sale/app/store/make_awaitable_dialog";
import { GuestDetail } from "@lo_pos_guest_info/number_of_guest_popup/guest_detail_popup";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { _t } from "@web/core/l10n/translation";

export class NumberOfGuest extends Component {
    static components = { Dialog };
    static props = {
        close: Function,
        getPayload: { type: Function },
        table_order: { type: Object, optional: false },
    };

    async setup() {
        super.setup();
        this.dialog = useService("dialog");
        this.pos = usePos();
        this.state = useState({
            male:  this.props.table_order.no_of_male || 0,
            female: this.props.table_order.no_of_female || 0,
            total:  this.props.table_order.customer_count || 1});
    }

    async confirm (ev){
        if (this.state.total > 0){
            let array = [];
            for (let i = 1; i <= this.state.total; i++) {
                array.push(i);
            }
            this.props.table_order.no_of_male = this.state.male
            this.props.table_order.no_of_female = this.state.female
            this.props.table_order.customer_count = this.state.total
            if(!this.props.table_order.no_of_male && !this.props.table_order.no_of_female){
                this.props.table_order.no_of_male = this.props.table_order.customer_count
            }
            const details = await makeAwaitable(this.dialog, GuestDetail, {total_guest: array, current_order: this.props.table_order});
            if (details){
                if(details.skip){
                    this.props.close();
                    this.pos.showScreen("ProductScreen");
                    return;
                }
                this.props.getPayload(details);
                this.props.close();
            }
        }
        else {
            ask(this.dialog, {
                title: _t("Invalid Guest Count"),
                body: _t("The number of guests cannot be 0.\nPlease enter a valid number."),
            });
        }
    }

    async OnChangeMale(ev){
        this.state.male = parseFloat(ev.target.value)
        this.state.total = parseFloat(this.state.male) + parseFloat(this.state.female)
    }

    async OnChangeFemale(ev){
        this.state.female = parseFloat(ev.target.value)
        this.state.total = parseFloat(this.state.male) + parseFloat(this.state.female)
    }

    async OnChange(ev){
        this.state.total = parseFloat(ev.target.value)
        this.state.male = 0
        this.state.female = 0
    }

    async skip(){
        this.props.table_order.no_of_male = this.state.male
        this.props.table_order.no_of_female = this.state.female
        this.props.table_order.customer_count = this.state.total
        if(!this.props.table_order.no_of_male && !this.props.table_order.no_of_female){
                this.props.table_order.no_of_male = this.props.table_order.customer_count
        }
        this.props.close();
        this.pos.showScreen("ProductScreen");
    }

    static template = xml`
        <Dialog title="'No of Guest'" >
            <t class="'body'">
                <div class="row mt-2">
                    <div class="col-md-2 mt-2 o_colored_level">
                        <label for="male_guest" class="o_default_snippet_text">No of Male: </label>
                    </div>
                    <div class="col-md-2 mt-2 o_colored_level">
                        <input class="form-control" style="border-color: #838383;" name="male_guest" type="number" t-att-value="state.male" t-on-change="OnChangeMale"/>
                    </div>

                    <div class="col-md-2  mt-2 o_colored_level">
                        <label for="female_guest" class="o_default_snippet_text">No of Female: </label>
                    </div>
                    <div class="col-md-2  mt-2 o_colored_level">
                        <input class="form-control" style="border-color: #838383;" name="female_guest" type="number" t-att-value="state.female" t-on-change="OnChangeFemale"/>
                    </div>

                    <div class="col-md-2  mt-2 o_colored_level">
                        <label for="total_guest" class="o_default_snippet_text">No of Guest: </label>
                    </div>
                    <div class="col-md-2  mt-2 o_colored_level">
                        <input class="form-control" style="border-color: #838383;" name="total_guest" type="number" t-att-value="state.total" t-on-change="OnChange"/>
                    </div>
                </div>
            </t>
            <t t-set-slot="footer">
                <div class="'modal-footer-left d-flex gap-2'">
                    <div class="'modal-footer-left d-flex gap-2'">
                        <button style="margin-right: 10px" class="button highlight btn btn-lg btn-primary" t-on-click="confirm">Next</button>
                        <button style="margin-right: 10px" class="button btn btn-lg btn-secondary" t-on-click="props.close">Close</button>
                        <button class="button btn btn-lg btn-secondary" t-on-click="skip">Skip</button>
                    </div>
                </div>
            </t>
        </Dialog>
    `;

}
