/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { ControlButtons,ControlButtonsPopup } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
patch(ProductScreen.prototype, {
    setup() {
        super.setup();
        this.sidebar = useService("sidebar");
    },
    displayAllControlPopup() {
        if(!this.pos.config.is_control_button_side_bar){
            this.dialog.add(ControlButtonsPopup);
        }else{
            this.sidebar.add(ControlButtons, {
                showRemainingButtons: true,
                onClickMore: () => {},
            });
        }

    },
});
