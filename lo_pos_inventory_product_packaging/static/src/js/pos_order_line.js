import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { patch } from "@web/core/utils/patch";

patch(PosOrderline.prototype, {
    setOptions(options) {
        if (options.uiState) {
            this.uiState = { ...this.uiState, ...options.uiState };
        }

        if (options.code) {
            const code = options.code;
            const blockMerge = ["weight", "quantity", "discount"];
            const product_packaging_by_barcode =
                this.models["product.packaging"].getAllBy("barcode");

            if (blockMerge.includes(code.type)) {
                this.set_quantity(code.value);
            } else if (code.type === "price") {
                this.set_unit_price(code.value);
                this.price_type = "manual";
            }

            if(!this.product_id.is_pack_product && product_packaging_by_barcode[code.code]) {
                this.set_quantity(product_packaging_by_barcode[code.code].qty);
            }
        }

        this.set_unit_price(this.price_unit);
    }
});