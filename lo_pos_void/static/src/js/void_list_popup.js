import { Dialog } from "@web/core/dialog/dialog";
import { Component, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";


export class voidLineListPopup extends Component {
    static components = { Dialog };
    static template = "lo_pos_void.voidLineListPopup";
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
    }

    close() {
        this.props.close();
    }
}
