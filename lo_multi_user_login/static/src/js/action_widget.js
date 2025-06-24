import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";

import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";

/**
 * @props partner
 */
patch(ActionpadWidget.prototype, {

    async submitOrder() {
        await super.submitOrder(...arguments);

        await rpc('/web/dataset/call_kw', { model: 'pos.order', method: 'send_kitchen',args: [[],this.currentOrder.id],kwargs: {},});
    },

});
