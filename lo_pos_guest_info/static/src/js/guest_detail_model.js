/* @odoo-module */

import { registry } from "@web/core/registry";
import { Base } from "@point_of_sale/app/models/related_models";

export class GuestDetailModel extends Base {
    static pythonModel = "guest.detail";

    setup(vals) {
        super.setup(vals);
    }
}

registry.category("pos_available_models").add(GuestDetailModel.pythonModel, GuestDetailModel);
