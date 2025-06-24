import { _t } from "@web/core/l10n/translation";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";
import { voidLineListPopup } from "./void_list_popup";
import { voidReasonPopup } from "./void_reason";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";

patch(ControlButtons.prototype, {
    setup() {
        super.setup(...arguments);
        var order_line = this.pos.get_order().get_selected_orderline()
        this.visible_void_button = this.pos.config.on_void
        this.voidListLen = this.pos.get_order().void_ids.length > 0
        if (order_line != undefined && order_line.status){
            if (order_line.status == 'confirm'){
                this.button_void = true
            }
            else{
                this.button_void = false
            }
        }
        else{
            this.button_void = false
        }
    },
    async clickvoid(){
        var order_line = this.pos.get_order().get_selected_orderline()
        if (order_line != undefined){
        const selectionList = this.pos.config.void_reasons_ids.map((reason) => ({
            id: reason.id,
            label: reason.name,
            item: reason,
        }));
         const payload = await makeAwaitable(this.dialog, voidReasonPopup, {
            title: _t("Select Void Reason"),
            list: selectionList,
        });
       }
        else{
        this.dialog.add(AlertDialog, {
            title: _t("Validation Error!"),
            body: _t(
                "Please Select Order Line."
            ),
        });
        return;
    }
    },

    async ShowVoidList(){
        var void_ids = this.pos.get_order().void_ids
        const payload = await makeAwaitable(this.dialog, voidLineListPopup, {
            title: _t("Void Line List"),
            list: void_ids,
        });
    }
});
