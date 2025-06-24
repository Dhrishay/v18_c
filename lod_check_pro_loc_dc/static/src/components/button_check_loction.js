
/** @odoo-module **/

import MainComponent from '@stock_barcode/components/main';
import { MainMenu } from '@stock_barcode/main_menu/main_menu';
import { patch } from "@web/core/utils/patch";


patch(MainComponent.prototype, {
    async openFreeLocation() {
        var url = '/check_free_location';
        window.location.href = url
    }
    ,

    async clickConfirmMapping() {
        if(this.resId){
            await this.orm.call('stock.picking', "action_confirm_mapping", [this.resId], {});
        }
        
    }
});
