import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { reactive } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

patch(ProductScreen.prototype, {

    // async addProductToOrder(product) {
    //     try {
    //         // Add product line to the current order
    //         await reactive(this.pos).addLineToCurrentOrder({ product_id: product }, {});
    
    //         // Sync orders only once after product is added, if needed
    //         await this.pos.syncAllOrders();
    
    //         // Send notification if currentOrder exists
    //         if (this.currentOrder) {
    //             await rpc('/web/dataset/call_kw', {
    //                 model: 'pos.order',
    //                 method: 'send_notification',
    //                 args: [[], this.currentOrder.id, this.currentOrder.uuid],
    //                 kwargs: {},
    //             });
    //         }
    //     } catch (error) {
    //         // Handle any errors that occur in the async operations
    //         console.error('Error adding product to order:', error);
    //     }
    // }
    

});
