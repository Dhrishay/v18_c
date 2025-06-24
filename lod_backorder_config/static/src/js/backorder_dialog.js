/** @odoo-module **/

import { BackorderDialog } from '@stock_barcode/components/backorder_dialog';
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { BackOrderLocationAutocomplete } from "./backorder_location_autocomplete";

BackorderDialog.props = {
    ...BackorderDialog.props,
    backOrderLocations: Array,
    id: { type: Number, optional: true },
    backOrder_id: { type: Number, optional: true },
    backOrder_name: { type: String, optional: true },
};
BackorderDialog.components = {
    ...BackorderDialog.components
};

patch(BackorderDialog.prototype, {



    async _onApply() {
        if (!this.props.id) {
            this.props.id = this.props.backOrder_id;
        }
        await this.props.onApply(this.props.id);
        await this.props.close();
    }
});


