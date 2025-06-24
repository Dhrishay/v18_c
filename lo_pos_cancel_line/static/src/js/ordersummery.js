import { _t } from "@web/core/l10n/translation";
import { OrderSummary } from "@point_of_sale/app/screens/product_screen/order_summary/order_summary";
import { patch } from "@web/core/utils/patch";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { rpc } from "@web/core/network/rpc";

patch(OrderSummary.prototype, {


    async _setValue(val) {
        const selectedLine = this.currentOrder.get_selected_orderline();
        if (!selectedLine) {
            return;
        }
        var restriction = this.pos.config.restrict_line_delete
        if (restriction == true){
            if (selectedLine.status != 'confirm' && selectedLine.status != 'waste' && selectedLine.status != 'void'){
                super._setValue(val);
            }else{
                if (selectedLine.status == 'waste'){
                    this.dialog.add(AlertDialog, {
                    title: _t("Invalid Opration"),
                    body: _t(
                        "This Line Already Waste"
                    ),
                });
                }else{
                this.dialog.add(AlertDialog, {
                    title: _t("Invalid Opration"),
                    body: _t(
                        "Order is Already Placed"
                    ),
                });
            }
            }
        }
        else{
             super._setValue(val);
        }
    },

});
