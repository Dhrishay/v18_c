import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { rpc } from "@web/core/network/rpc";

patch(PosStore.prototype, {
    /**
     * @override
     */
    async setup() {
        await super.setup(...arguments);
    
        // Helper function to add a pending order and sync
        const addPendingAndSync = (delay = 500) => {
            const order = this.get_order();
            if (order) {
                this.addPendingOrder([order.id]);
                setTimeout(() => {
                    this.syncAllOrders();
                }, delay);
            }
        };
    
        // Subscribe to "update_order_notification"
        this.bus.subscribe("update_order_notification", () => {
            addPendingAndSync();
            setTimeout(() => {
                this.data.models["pos.order.line"].readAll();
                this.data.models["pos.order"].readAll();
            }, 500);
        });
    
        // Subscribe to "switch_screen"
        this.bus.subscribe("switch_screen", (payload) => {
            if (payload.data.order) {
                this.showScreen(payload.data.screen);
                this.syncAllOrders();
            }
        });
    
        // Subscribe to "action_pad_update"
        this.bus.subscribe("action_pad_update", () => {
            addPendingAndSync(1000);
        });
    
        // Subscribe to "wast_from_backend"
        this.bus.subscribe("wast_from_backend", () => {
            addPendingAndSync(10000);
        });
    
        // Subscribe to "send_kitchen"
        this.bus.subscribe("send_kitchen", (payload) => {
            const order = this.get_order();
            if (order && payload.data && payload.data.order_id === order.id) {
                setTimeout(() => {
                    this.sendOrderInPreparationUpdateLastChange(order);
                }, 300);
            }
        });
    }
    



});
