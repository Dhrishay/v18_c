/** @odoo-module **/

import { PosData } from "@point_of_sale/app/models/data_service";
import { patch } from "@web/core/utils/patch";
import { Reactive, effect } from "@web/core/utils/reactive";
import { createRelatedModels } from "@point_of_sale/app/models/related_models";
import { registry } from "@web/core/registry";
import { Mutex } from "@web/core/utils/concurrency";
import { markRaw } from "@odoo/owl";
import { batched } from "@web/core/utils/timing";
import IndexedDB from "@point_of_sale/app/models/utils/indexed_db";
import { DataServiceOptions } from "@point_of_sale/app/models/data_service_options";
import { getOnNotified, uuidv4 } from "@point_of_sale/utils";
import { browser } from "@web/core/browser/browser";
import { ConnectionLostError, RPCError } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import DevicesSynchronisation from "@point_of_sale/app/store/devices_synchronisation";
//import { PosCollection, Order, Product } from "@point_of_sale/app/store/models";

patch(PosStore.prototype, {
    async afterProcessServerData() {
        const paidUnsyncedOrderIds = this.models["pos.order"]
            .filter((order) => order.isUnsyncedPaid)
            .map((order) => order.id);

        if (paidUnsyncedOrderIds.length > 0) {
            this.addPendingOrder(paidUnsyncedOrderIds);
        }

        // Adding the not synced paid orders to the pending orders
        const openOrders = this.data.models["pos.order"].filter((order) => !order.finalized);
        this.syncAllOrders();

        if (!this.config.module_pos_restaurant) {
            this.selectedOrderUuid = openOrders.length
                ? openOrders[openOrders.length - 1].uuid
                : this.add_new_order().uuid;
        }

        this.markReady();
        this.showScreen(this.firstScreen);
        await this.deviceSync.readDataFromServer();
        this.deviceSync.loadProducts();
    }
});
patch(DevicesSynchronisation.prototype, {
    async loadProducts() {
        console.log("**************************************************")

        if(this.pos.config.limited_products_loading && this.pos.config.product_load_background){
            let page = 0;
            let product_model = 'product.product';
            let products = [];
            let data = {};
            do {
                products = await this.pos.data.call("product.product", "pos_load_data", [
                    [],
                    this.pos.config.current_session_id.id,
                    page * this.pos.config.limited_product_count,
                    this.pos.config.limited_product_count,
                ]);
                console.log("products--------------------------",products)
                for (const [model, values] of Object.entries(products)) {
                    data[model] = values.data;
                }
                this.models.loadData(data, ['product.product'], true, true);
                page += 1;
            } while(products['product.product'] && products['product.product'].data && products['product.product'].data.length >= this.pos.config.limited_product_count);

        }
        if(this.pos.config.limited_partners_loading && this.pos.config.partner_load_background){
            let page = 0;
            let product_model = 'res.partner';
            let customers = [];
            let data = {};
            do {
                customers = await this.pos.data.call("res.partner", "pos_load_data", [
                    [],
                    this.pos.config.id,
                    page * this.pos.config.limited_partner_count,
                    this.pos.config.limited_partner_count,
                ]);
                for (const [model, values] of Object.entries(customers)) {
                    data[model] = values.data;
                }
                this.models.loadData(data, ['res.partner'], true, true);
                page += 1;

            } while(customers['res.partner'] && customers['res.partner'].data && customers['res.partner'].data.length >= this.pos.config.limited_partner_count);

        }

    }
});