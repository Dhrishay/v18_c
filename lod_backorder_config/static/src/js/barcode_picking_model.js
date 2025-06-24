/** @odoo-module **/

import BarcodePickingModel from "@stock_barcode/models/barcode_picking_model";
import { patch } from "@web/core/utils/patch";
import { BackorderDialog } from '@stock_barcode/components/backorder_dialog';
import { _t } from "@web/core/l10n/translation";


patch(BarcodePickingModel.prototype, {


    async validate() {
            
            if (this.config.restrict_scan_dest_location == 'mandatory' &&
                !this.lastScanned.destLocation && this.selectedLine) {
                return this.notification(_t("Destination location must be scanned"), { type: "danger" });
            }
            if (this.config.lines_need_to_be_packed &&
                this.currentState.lines.some(line => this._lineNeedsToBePacked(line))) {
                return this.notification(_t("All products need to be packed"), { type: "danger" });
            }
            await this._setUser();
            if (this.config.create_backorder === 'ask') {
                // If there are some uncompleted lines, displays the backorder dialog.
                const uncompletedLines = [];
                const alreadyChecked = [];
                let atLeastOneLinePartiallyProcessed = false;
                for (let line of this.currentState.lines) {
                    
                    line = this._getParentLine(line) || line;
                    if (alreadyChecked.includes(line.virtual_id)) {
                        continue;
                    }
                    // Keeps track of already checked lines to avoid to check multiple times grouped lines.
                    alreadyChecked.push(line.virtual_id);
                    let qtyDone = line.qty_done;
                    if (qtyDone < line.reserved_uom_qty) {
                        // Checks if another move line shares the same move id and adds its quantity done in that case.
                        qtyDone += this.currentState.lines.reduce((additionalQtyDone, otherLine) => {
                            return otherLine.product_id.id === line.product_id.id
                                && otherLine.move_id === line.move_id
                                && !otherLine.reserved_uom_qty ?
                                additionalQtyDone + otherLine.qty_done : additionalQtyDone
                        }, 0);
                        if (qtyDone < line.reserved_uom_qty) { // Quantity done still insufficient.
                            uncompletedLines.push(line);
                        }
                    }
                    atLeastOneLinePartiallyProcessed = atLeastOneLinePartiallyProcessed || (qtyDone > 0);
                }
                if (this.showBackOrderDialog && atLeastOneLinePartiallyProcessed && uncompletedLines.length) {
                    this.trigger("playSound");
                    if (this.record.picking_type_code != 'incoming') {

                        return this.dialogService.add(BackorderDialog, {
                                        displayUoM: this.groups.group_uom,
                                        uncompletedLines,
                                        onApply: () => super.validate(),
                                    });
                    }

                    else{


                        return this.dialogService.add(BackorderDialog, {
                            displayUoM: this.groups.group_uom,
                            uncompletedLines,
                            backOrderLocations: this.config.backorder_all_locations,
                            backOrder_id: this.config.backorder_location_id,
                            backOrder_name: this.config.backorder_location_name,
                            onApply: (id) => {
                                this.validate_record(id)},
                        });


                    }

                    
                  
                }
            }
            if (this.record.return_id) {
                this.validateContext = {...this.validateContext, picking_ids_not_to_backorder: this.resId};
            }
            if (this.shouldOpenSignatureModal) {
                this.openSignatureDialog(true);
                return;
            }
            return await super.validate();
        }
    
});

