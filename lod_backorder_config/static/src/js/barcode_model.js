/** @odoo-module **/


import BarcodeModel from '@stock_barcode/models/barcode_model';
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(BarcodeModel.prototype, {


    async validate_record(id) {
        await this.save();
        const context = this.validateContext;
        Object.assign(this.validateContext, { backorder_location: id });

        context['barcode_trigger'] = true;
        const action = await this.orm.call(
            this.resModel,
            this.validateMethod,
            [this.recordIds],
            { context },
        );
        const options = {
            onClose: ev => this._closeValidate(ev)
        };
        if (action && (action.res_model || action.type == "ir.actions.client")) {
            if (action.type == "ir.actions.client") {
                action.params = Object.assign(action.params || {}, options)
            }
            this.trigger("playSound");
            return this.action.doAction(action, options);
        }
        return options.onClose();
    },

    async _processBarcode(barcode) {
        let barcodeData = {};
        let currentLine = false;
        // Creates a filter if needed, which can help to get the right record
        // when multiple records have the same model and barcode.
        const filters = {};
        if (this.selectedLine && this.selectedLine.product_id.tracking !== 'none') {
            filters['stock.lot'] = {
                product_id: this.selectedLine.product_id.id,
            };
        }
        // Constrain DB reads to records which belong to the company defined on the open operation
        filters['all'] = {
            company_id: [false].concat(this._getCompanyId() || []),
        };
        try {
            barcodeData = await this._parseBarcode(barcode, filters);
            if (this._shouldSearchForAnotherLot(barcodeData, filters)) {
                // Retry to parse the barcode without filters in case it matches an existing
                // record that can't be found because of the filters
                const lot = await this.cache.getRecordByBarcode(barcode, 'stock.lot');
                if (lot) {
                    Object.assign(barcodeData, { lot, match: true });
                }
            }
        } catch (parseErrorMessage) {
            barcodeData.error = parseErrorMessage;
        }

        // Keep in memory every scans.
        this.scanHistory.unshift(barcodeData);

        if (barcodeData.match) { // Makes flash the screen if the scanned barcode was recognized.
            this.trigger('flash');
        }

        // Process each data in order, starting with non-ambiguous data type.
        if (barcodeData.action) { // As action is always a single data, call it and do nothing else.
            return await barcodeData.action();
        }

        if (barcodeData.packaging) {
            Object.assign(barcodeData, this._retrievePackagingData(barcodeData));
        }

        // Depending of the configuration, the user can be forced to scan a specific barcode type.
        const check = this._checkBarcode(barcodeData);
        if (check.error) {
            return this.notification(check.message, { title: check.title, type: "danger" });
        }

        if (barcodeData.product) { // Remembers the product if a (packaging) product was scanned.
            this.lastScanned.product = barcodeData.product;
        }

        if (barcodeData.lot && !barcodeData.product) {
            Object.assign(barcodeData, this._retrieveTrackingNumberInfo(barcodeData.lot));
        }

        await this._processLocation(barcodeData);
        await this._processPackage(barcodeData);
        if (barcodeData.stopped) {
            // TODO: Sometime we want to stop here instead of keeping doing thing,
            // but it's a little hacky, it could be better to don't have to do that.
            return;
        }

        if (barcodeData.weight) { // Convert the weight into quantity.
            barcodeData.quantity = barcodeData.weight.value;
        }

        // If no product found, take the one from last scanned line if possible.
        if (!barcodeData.product) {
            if (barcodeData.quantity) {
                currentLine = this.selectedLine || this.lastScannedLine;
            } else if (this.selectedLine && this.selectedLine.product_id.tracking !== 'none') {
                currentLine = this.selectedLine;
            } else if (this.lastScannedLine && this.lastScannedLine.product_id.tracking !== 'none') {
                currentLine = this.lastScannedLine;
            }
            if (currentLine) { // If we can, get the product from the previous line.
                const previousProduct = currentLine.product_id;
                // If the current product is tracked and the barcode doesn't fit
                // anything else, we assume it's a new lot/serial number.
                if (previousProduct.tracking !== 'none' &&
                    !barcodeData.match && this.canCreateNewLot) {
                    this.trigger('flash');
                    barcodeData.lotName = barcode;
                    barcodeData.product = previousProduct;
                }
                if (barcodeData.lot || barcodeData.lotName ||
                    barcodeData.quantity) {
                    barcodeData.product = previousProduct;
                }
            }
        }
        let { product } = barcodeData;
        if (!product && barcodeData.match && this.parser.nomenclature.is_gs1_nomenclature) {
            // Special case where something was found using the GS1 nomenclature but no product is
            // used (eg.: a product's barcode can be read as a lot is starting with 21).
            // In such case, tries to find a record with the barcode by by-passing the parser.
            barcodeData = await this._fetchRecordFromTheCache(barcode, filters);
            if (barcodeData.packaging) {
                Object.assign(barcodeData, this._retrievePackagingData(barcodeData));
            } else if (barcodeData.lot) {
                Object.assign(barcodeData, this._retrieveTrackingNumberInfo(barcodeData.lot));
            }
            if (barcodeData.product) {
                product = barcodeData.product;
            } else if (barcodeData.match) {
                await this._processPackage(barcodeData);
                if (barcodeData.stopped) {
                    return;
                }
            }
        }
        if (!product) { // Product is mandatory, if no product, raises a warning.
            return this.noProductToast(barcodeData);
        } else if (barcodeData.lot && barcodeData.lot.product_id !== product.id) {
            delete barcodeData.lot; // The product was scanned alongside another product's lot.
        }
        if (barcodeData.weight) { // the encoded weight is based on the product's UoM
            barcodeData.uom = this.cache.getRecord('uom.uom', product.uom_id);
        }

        // Searches and selects a line if needed.
        if (!currentLine || this._shouldSearchForAnotherLine(currentLine, barcodeData)) {
            currentLine = this._findLine(barcodeData);
        }

        // Default quantity set to 1 by default if the product is untracked or
        // if there is a scanned tracking number.
        if (product.tracking === 'none' || barcodeData.lot || barcodeData.lotName || this._incrementTrackedLine()) {
            const hasUnassignedQty = currentLine && currentLine.qty_done && !currentLine.lot_id && !currentLine.lot_name;
            const isTrackingNumber = barcodeData.lot || barcodeData.lotName;
            const defaultQuantity = isTrackingNumber && hasUnassignedQty ? 0 : 1;
            barcodeData.quantity = barcodeData.quantity || defaultQuantity;
            if (product.tracking === 'serial' && barcodeData.quantity > 1 && (barcodeData.lot || barcodeData.lotName)) {
                barcodeData.quantity = 1;
                this.notification(
                    _t(`A product tracked by serial numbers can't have multiple quantities for the same serial number.`),
                    { type: 'danger' }
                );
            }
        }

        if ((barcodeData.lotName || barcodeData.lot) && product) {
            const lotName = barcodeData.lotName || barcodeData.lot.name;
            for (const line of this.currentState.lines) {
                if (line.product_id.id !== product.id) {
                    continue; // The same SN can be scanned for different product.
                }
                if (line.product_id.tracking === "serial" && this.getQtyDone(line) !== 0 &&
                    this.getlotName(line) === lotName) {
                    return this.notification(
                        _t("The scanned serial number %s is already used.", lotName),
                        { type: 'danger' }
                    );
                }
            }
            // Prefills `owner_id` and `package_id` if possible.
            const prefilledOwner = (!currentLine || (currentLine && !currentLine.owner_id)) && this.groups.group_tracking_owner && !barcodeData.owner;
            const prefilledPackage = (!currentLine || (currentLine && !currentLine.package_id)) && this.groups.group_tracking_lot && !barcodeData.package;
            if (this.useExistingLots && (prefilledOwner || prefilledPackage)) {
                const lotId = (barcodeData.lot && barcodeData.lot.id) || (currentLine && currentLine.lot_id && currentLine.lot_id.id) || false;
                const locationId = (currentLine && currentLine.location_id && currentLine.location_id.id) || false;
                const params = {
                    lot_id: lotId,
                    lot_name: (!lotId && barcodeData.lotName) || false,
                };
                let quants = await this.cache.getQuants(product, locationId, params);
                if (quants.length && quants.length > 1 && (prefilledPackage || prefilledOwner)) {
                    // If we have multiple matching quants and we use package and/or consigment,
                    // give priority to the quants with a package or an owner.
                    const filteredQuants = quants.filter((quant) => {
                        return quant.package_id || quant.owner_id;
                    });
                    quants = filteredQuants.length ? filteredQuants : quants;
                }
                if (quants && quants.length === 1) {
                    const quant = quants[0];
                    if (prefilledPackage && quant.package_id) {
                        barcodeData.package = this.cache.getRecord("stock.quant.package", quant.package_id);
                    }
                    if (prefilledOwner && quant.owner_id) {
                        barcodeData.owner = this.cache.getRecord("res.partner", quant.owner_id);
                    }
                }
            }
        }

        // Updates or creates a line based on barcode data.
        if (currentLine) { // If line found, can it be incremented ?
            let exceedingQuantity = 0;
            if (product.tracking !== 'serial' && barcodeData.uom && barcodeData.uom.category_id == currentLine.product_uom_id.category_id) {
                // convert to current line's uom
                barcodeData.quantity = (barcodeData.quantity / barcodeData.uom.factor) * currentLine.product_uom_id.factor;
                barcodeData.uom = currentLine.product_uom_id;
            }
            // Checks the quantity doesn't exceed the line's remaining quantity.
            if (currentLine.reserved_uom_qty && product.tracking === 'none') {
                const remainingQty = currentLine.reserved_uom_qty - currentLine.qty_done;
                if (barcodeData.quantity > remainingQty && this._shouldCreateLineOnExceed(currentLine)) {
                    // In this case, lowers the increment quantity and keeps
                    // the excess quantity to create a new line.
                    exceedingQuantity = barcodeData.quantity - remainingQty;
                    barcodeData.quantity = remainingQty;
                }
            }
            if (barcodeData.quantity > 0 || barcodeData.lot || barcodeData.lotName) {
                const fieldsParams = this._convertDataToFieldsParams(barcodeData);
                if (barcodeData.uom) {
                    fieldsParams.uom = barcodeData.uom;
                }
                await this.updateLine(currentLine, fieldsParams);
                this.trigger("playSound", "success");
            }
            if (exceedingQuantity) { // Creates a new line for the excess quantity.
                const message = _t(
                    "Quantity exceeds the line's remaining quantity. " ,
                );
                this.notification(message, { type: "danger" });
                return false;
            }
        } else { // No line found, so creates a new one.
            const fieldsParams = this._convertDataToFieldsParams(barcodeData);
            if (barcodeData.uom) {
                fieldsParams.uom = barcodeData.uom;
            }
            if (this.createSingleLinesForPackaging(barcodeData)) {
                for (let lineCount = 0; lineCount < barcodeData.packaging.qty; lineCount++) {
                    currentLine = await this.createNewLine({fieldsParams});
                }
            } else {
                currentLine = await this.createNewLine({fieldsParams});
            }
            if(currentLine){
                this.trigger("playSound", "success");
            }
        }

        // And finally, if the scanned barcode modified a line, selects this line.
        if (currentLine) {
            this._selectLine(currentLine);
        }

        const matchedURI = barcode.match(/^urn:.*$/);
        if (matchedURI) {
            // If the process goes right and the scanned barcode is an URI, add
            // it to the cache to avoid scanning it a second time.
            this.uriCache.add(barcode);
        }
        this.trigger('update');
    }

}
)
