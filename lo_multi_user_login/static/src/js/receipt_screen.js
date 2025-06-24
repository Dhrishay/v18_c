// Part of Odoo. See LICENSE file for full copyright and licensing details.
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";

patch(ReceiptScreen.prototype, {

    orderDone() {
        this.currentOrder.uiState.screen_data.value = "";
        this.currentOrder.uiState.locked = true;
        this._addNewOrder();
        this.pos.searchProductWord = "";
        const { name, props } = this.nextScreen;
        rpc('/web/dataset/call_kw', {model: 'pos.order', method: 'switch_screen',args: [[],name,this.currentOrder.id],kwargs: {},});
        this.pos.showScreen(name, props);
    }
});
