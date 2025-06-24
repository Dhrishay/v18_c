/* @odoo-module */

import { Orderline } from "@pos_preparation_display/app/components/orderline/orderline";
import { patch } from "@web/core/utils/patch";
import { useState } from "@odoo/owl";


patch(Orderline.prototype, {
    async setup() {
        super.setup();
        this.state = useState({
            showIngredients: false,
        });

        const data = await this.orm.call(
            "product.product",
            "get_bom_data",
            [this.props.orderline.productId],
            {}
        );

        this.props.orderline.is_ingredients = false
        if (data){
            this.props.orderline.is_ingredients = true
            this.props.orderline.ingredients = data
        }
    },

    // Toggle the visibility (Hide and Show Ingredients)
    toggleIngredients() {
        this.state.showIngredients = !this.state.showIngredients;
    }
});
