import { Chrome } from "@point_of_sale/app/pos_app";
import { patch } from "@web/core/utils/patch";

patch(Chrome.prototype, {
    sendOrderToCustomerDisplay(selectedOrder, scaleData) {
        const customerDisplayData = selectedOrder.getCustomerDisplayData();
        customerDisplayData.isScaleScreenVisible = this.pos.isScaleScreenVisible;
        if (scaleData) {
            customerDisplayData.scaleData = {
                productName: scaleData.productName,
                uomName: scaleData.uomName,
                uomRounding: scaleData.uomRounding,
                productPrice: scaleData.productPrice,
            };
        }
        customerDisplayData.weight = this.pos.scaleWeight;
        customerDisplayData.tare = this.pos.scaleTare;
        customerDisplayData.totalPriceOnScale = this.pos.totalPriceOnScale;
        customerDisplayData.qr_code = selectedOrder.qr_code;

        if (this.pos.config.customer_display_type === "local") {
            this.customerDisplayChannel.postMessage(customerDisplayData);
        }
        if (this.pos.config.customer_display_type === "remote") {
            this.pos.data.call("pos.config", "update_customer_display", [
                [this.pos.config.id],
                customerDisplayData,
                this.pos.config.access_token,
            ]);
        }
        if (this.pos.config.customer_display_type === "proxy") {
            const proxyIP = this.pos.getDisplayDeviceIP();
            fetch(`${deduceUrl(proxyIP)}/hw_proxy/customer_facing_display`, {
                method: "POST",
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    params: {
                        action: "set",
                        data: customerDisplayData,
                    },
                }),
            }).catch(() => {
                console.log("Failed to send data to customer display");
            });
        }
    }
});
