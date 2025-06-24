import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { patch } from "@web/core/utils/patch";

patch(PosOrderline.prototype, {

    setup() {
        super.setup(...arguments);
        this.barcode = this.product_id?.barcode || "";
    },    

    getDisplayData() {
        return {
            ...super.getDisplayData(),
            barcode: this.get_product()?.barcode || "",            
            cashier_name: this.cashier_id ? this.cashier_id.name : "",
            show_product_line: this.config.show_employee,
            status: this.status != false ? this.status : "",
        };
    },
});

patch(Orderline, {
    props: {
        ...Orderline.props,
        line: {
            ...Orderline.props.line,
            shape: {
                ...Orderline.props.line.shape,
                barcode: { type: String, optional: true },
                cashier_name: { type: String, optional: true },
                status: { type: String, optional: true },
                show_product_line: { type: Boolean, optional: true },
            },
        },
    },
});
