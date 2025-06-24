/** @odoo-module **/
import { Component } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { floatIsZero, roundPrecision } from "@web/core/utils/numbers";


export class MultiCurrencyPopup extends Component {
    static template = "lo_multi_currency_pos.MultiCurrencyPopup";
    static components = { Dialog };
    static props = {
        close: Function,
        payment_method: { type: Object, optional: false },
        getPayload: { type: Function },
    };

    setup() {
        super.setup();
        this.pos = usePos();
        this.values = this.env.services.pos.multicurrencypayment;
        this.default_currency = this.env.services.pos.currency;
        this.selected_curr_name = this.values[0].name;
        this.AmountTotal = this.env.services.pos.get_order().get_due();
        this.selected_rate = this.values[0].rate
        this.inverse_rate = this.values[0].inverse_rate
        this.symbol = this.values[0].symbol
        this.amount_total_currency = (this.inverse_rate * this.AmountTotal).toFixed(4)
        if (this.pos.config.cash_rounding) {
            var cash_rounding = this.pos.config.rounding_method.rounding;
            this.AmountTotal = roundPrecision(this.pos.get_order().get_due(), cash_rounding);
        }
    }

    getValues(event) {
        this.selected_value = this.values.find((val) => val.id === parseFloat(event.target.value));
        this.selected_curr_name = this.selected_value.name;
        this.selected_rate = this.selected_value.rate
        this.inverse_rate = this.selected_value.inverse_rate
        this.symbol = this.selected_value.symbol
        this.amount_total_currency = (this.inverse_rate * this.AmountTotal).toFixed(4);
        this.render();
    }

    //    getPayload() {
    //        return {
    //            currency_name: this.selected_curr_name,
    //            selected_rate: this.selected_rate,
    //            inverse_rate: this.inverse_rate,
    //            symbol: this.symbol,
    //        }
    //    }

    confirm(ev) {
        this.props.getPayload({
            currency_name: this.selected_curr_name,
            selected_rate: this.selected_rate,
            inverse_rate: this.inverse_rate,
            symbol: this.symbol,
        })
        this.props.close()
    }
}
