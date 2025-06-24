import { Dialog } from "@web/core/dialog/dialog";
import { Component, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
//import { SERIALIZABLE_MODELS } from "@point_of_sale/app/models/related_models";
import { serializeDateTime } from "@web/core/l10n/dates";
import { rpc } from "@web/core/network/rpc";

//SERIALIZABLE_MODELS.push("pos.void.reason.history")

export class voidReasonPopup extends Component {
    static components = { Dialog };
    static template = "lo_pos_void.voidReasonPopup";
    static props = {
        title: { type: String, optional: true },
        list: { type: Array, optional: true },
        getPayload: Function,
        close: Function,
    };

    async setup() {
        super.setup();
        this.pos = usePos();
        this.dialog = useService("dialog");
        this.state = useState({
            selectedId:null
        });
        this.visible_scrap_button = this.pos.config.scrap_product
    }

    async onClickReason(ev){
        const option_id = document.querySelectorAll('.reason_select_select')[0].value;
        this.state.selectedId = parseInt(option_id)
    }

//
    async confirm(ev) {
    try {
        // Get the selected reason and additional note
        const option_id = document.querySelector('.reason_select_select')?.value;
        const reason_extra = document.querySelector('.extra_reason_note')?.value;
        const order = this.pos.get_order();
        const order_line = order?.get_selected_orderline();

        // Ensure required values are present
        if (!option_id || !order || !order_line || order_line.status === 'void') {
            console.warn("Required information is missing or the order line is already void.");
            return;
        }

        // Prepare values for void reason history
        const selectedReason = this.pos.data.records['void.reasons'].get(parseInt(option_id));
        const values = {
            pos_order_id: order.id,
            reason_id: selectedReason?.id,
            session_id: this.pos.session.id,
            product_id: order_line.get_product().id,
            price: order_line.get_product().lst_price,
            order_no: order.pos_reference,
            table_no: order.table_id?.table_number || '',
            extra_note: reason_extra,
            date: serializeDateTime(luxon.DateTime.now()),
            pos_config_id: this.pos.config.id,
            user_id: order.user_id?.id || false,
            employee_id: order.employee_id?.id || false,
            qty: order_line.get_quantity(),
            status: 'void',
            product_uom_id: order_line.product_id.uom_id.id,
        };

        // Create void reason history and update order line status
        await rpc("/web/dataset/call_kw/pos.void.reason.history/create", {
            model: 'pos.void.reason.history',
            method: 'create',
            args: [values],
            kwargs: {},
        });

        await rpc("/web/dataset/call_kw/pos.order.line/write", {
            model: 'pos.order.line',
            method: 'write',
            args: [order_line.id, { status: 'void' }],
            kwargs: {},
        });

        // Handle voided order line removal after a short delay
        setTimeout(async () => {
            const voidedLine = order.lines.find(line => line.id === order_line.id);
            if (voidedLine) {
                await order.removeOrderline(voidedLine);
                await rpc('/web/dataset/call_kw', {
                    model: 'pos.order',
                    method: 'action_pad_update',
                    args: [[]],
                    kwargs: {},
                });
            }
        }, 1000);



        this.props.close();


    } catch (error) {
       await this.pos.syncAllOrders();

    }
    }


    async confirm_with_scrap(ev) {
        console.log("]x]]]x]xxxxxxxxxxxxxxxxx");
        const order = this.pos.get_order();
        const option_id = document.querySelectorAll('.reason_select_select')[0].value;
        this.state.selectedId = parseInt(option_id)
        const reason_extra = document.querySelectorAll('.extra_reason_note')[0].value
        var order_line = this.pos.get_order().get_selected_orderline()
        await rpc('/web/dataset/call_kw', {model: 'pos.order.line', method: 'create_scrap_from_pos',
            args: [[], order.id,order_line.id],
            kwargs: {},
        });
        if (this.state.selectedId && order_line && order){
            const values = {
                order_id:order,
                reason_id:this.pos.data.records['void.reasons'].get(parseInt(this.state.selectedId)),
                session_id: this.pos.session,
                product_id: order_line.get_product(),
                price: order_line.get_product().lst_price,
                order_no: order.pos_reference,
                table_no: order.table_id.table_number,
                date: serializeDateTime(luxon.DateTime.now()),
                pos_config_id: this.pos.config,
                extra_note: reason_extra
            }
            order.removeOrderline(order_line);
            const line = this.pos.data.models["pos.void.reason.history"].create({...values});
            order.void_ids.push(line)
            this.props.close();
        }
    }

    close() {
        this.props.close();
    }
}
