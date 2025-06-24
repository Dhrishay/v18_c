/* @odoo-module */

import { patch } from "@web/core/utils/patch";
import { FloorScreen } from "@pos_restaurant/app/floor_screen/floor_screen";
import { _t } from "@web/core/l10n/translation";
import { onMounted, onWillUnmount } from "@odoo/owl";

patch(FloorScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.state.tableTimers = {};
        this.timer = null;
        if (this.pos.config.table_timer_enable){
            onMounted(this.onMounted);
            onWillUnmount(this.onWillUnmount);
        }
    },

    onMounted() {
        this.timer = setInterval(() => {
            this.updateTimers();
        }, 1000);
    },

    onWillUnmount() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    },

    updateTimers() {
        const obj = {};
        if (this.activeTables){
            this.activeTables.forEach((table) => {
                const tableId = table.id;
                const orders = this.pos.getTableOrders(tableId);
                if (orders.length && orders[0].start_time && !orders[0].end_time) {
                    // Parse the datetime strings into Date objects
                    const start = new Date(orders[0].start_time.replace(" ", "T") + "Z");
                    const end = new Date(this.getUTCDateTime().replace(" ", "T") + "Z");

                    // Calculate the difference in milliseconds
                    const diffMs = end - start;

                    // Convert milliseconds to hours, minutes, and seconds
                    const hours = String(Math.floor(diffMs / (1000 * 60 * 60))).padStart(2, '0');
                    const minutes = String(Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))).padStart(2, '0');
                    const seconds = String(Math.floor((diffMs % (1000 * 60)) / 1000)).padStart(2, '0');

                    // Format the difference as HH:mm:ss
                    obj[tableId] = `${hours}:${minutes}:${seconds}`;
                } else {
                    obj[tableId] = "00:00:00";
                }
            });
        }

        Object.assign(this.state.tableTimers, obj);
    },

    getUTCDateTime() {
        const now = new Date();
        const year = now.getUTCFullYear();
        const month = String(now.getUTCMonth() + 1).padStart(2, '0');
        const date = String(now.getUTCDate()).padStart(2, '0');
        const hours = String(now.getUTCHours()).padStart(2, '0');
        const minutes = String(now.getUTCMinutes()).padStart(2, '0');
        const seconds = String(now.getUTCSeconds()).padStart(2, '0');
        return `${year}-${month}-${date} ${hours}:${minutes}:${seconds}`;
    },

    getTableTimer(table) {
        return this.state.tableTimers[table.id] || "00:00:00";
    },
});
