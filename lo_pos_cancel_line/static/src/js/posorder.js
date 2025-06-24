import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { rpc } from "@web/core/network/rpc";

patch(PosStore.prototype, {
    /**
     * @override
     */
    async sendOrderInPreparationUpdateLastChange(o, cancelled = false) {
    try {
        this.addPendingOrder([o.id]);

        // Sync all orders and find the target order
        const uuid = o.uuid;
        const orders = await this.syncAllOrders();
        const order = orders.find(order => order.uuid === uuid);

        if (!order) {
            console.error(`Order with UUID ${uuid} not found.`);
            return;
        }

        // Send order in preparation
        await this.sendOrderInPreparation(order, cancelled);

        // Update the status of relevant lines
        const linesToUpdate = order.lines.filter(line => line.status !== 'confirm');
        if (linesToUpdate.length > 0) {
            await Promise.all(
                linesToUpdate.map(line =>
                    rpc("/web/dataset/call_kw/pos.order.line/write", {
                        model: 'pos.order.line',
                        method: 'write',
                        args: [line.id, { status: 'confirm' }],
                        kwargs: {}
                    })
                )
            );
        }

        // Sync orders again after a delay
        setTimeout(() => this.syncAllOrders(), 1000);

        // Update order states
        const getOrder = uuid => this.models["pos.order"].getBy("uuid", uuid);
        const localOrder = getOrder(uuid);
        if (localOrder) {
            localOrder.updateLastOrderChange();
            this.addPendingOrder([order.id]);
            await this.syncAllOrders();
            localOrder.updateSavedQuantity();
        } else {
            console.error(`Local order with UUID ${uuid} not found in models.`);
        }
    } catch (error) {
        console.error("Error in sendOrderInPreparationUpdateLastChange:", error);
    }
}



});
