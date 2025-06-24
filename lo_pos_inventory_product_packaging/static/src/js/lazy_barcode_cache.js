/** @odoo-module **/

import LazyBarcodeCache from '@stock_barcode/lazy_barcode_cache';
import { rpc } from "@web/core/network/rpc";
import { patch } from "@web/core/utils/patch";
import BarcodeModel from "@stock_barcode/models/barcode_model";
import { _t } from "@web/core/l10n/translation";

patch(LazyBarcodeCache.prototype,{
    async getMissingRecords(params = {}) {
        if (!this.waitingFetch.length) {
            return; // Nothing to fetch.
        }
        params.barcodes_by_model = {};
        for (const data of this.waitingFetch) {
            const { barcode, model } = data;
            const keyCache = JSON.stringify([barcode, model, {}]);
            if (this.missingBarcodeKeyCache.has(keyCache)) {
                continue; // Avoid already fetched records.
            }
            this.missingBarcodeKeyCache.add(keyCache);
            if (!params.barcodes_by_model[model]) {
                params.barcodes_by_model[model] = [];
            }
            params.barcodes_by_model[model].push(barcode);
        }
        if (Object.keys(params.barcodes_by_model).length) {
            let resticateMissingRecod = false;
            const result = await rpc("/stock_barcode/get_specific_barcode_data", params);
            if('resticateMissingRecod' in result & result['resticateMissingRecod']){
                resticateMissingRecod = true;
            }
            delete result['resticateMissingRecod']
            this.setCache(result);
            if (params.forceUnrestrictedSearch) {
                // Create a list of every found records' barcode.
                const foundBarcodes = [];
                const missingBarcodes = new Set();
                for (const model of Object.keys(result)) {
                    for (const record of result[model]) {
                        foundBarcodes.push(record[this.barcodeFieldByModel[model]]);
                    }
                }
                if(!resticateMissingRecod){
                     // Put every searched barcodes with no matching records into a set.
                    for (const model of Object.keys(params.barcodes_by_model)) {
                        for (const barcode of params.barcodes_by_model[model]) {
                            if (!foundBarcodes.includes(barcode) && !this.missingBarcodesCache.has(barcode)) {
                                missingBarcodes.add(barcode);
                                this.missingBarcodesCache.add(barcode);
                            }
                        }
                    }
                    // If there are barcodes with no match, make a second RPC but this
                    // time, search for those barcodes with no assigned model.
                    if (missingBarcodes.size) {
                        const barcodes = [...missingBarcodes];
                        // Keep in cache the fact those barcodes were search so they won't be in the future.
                        for (const bc of barcodes) {
                            this.missingBarcodeKeyCache.add(JSON.stringify([bc, false, {}]));
                        }
                        const updatedParams = { ...params, barcodes };
                        delete updatedParams.barcodes_by_model;
                        const notRestrictedByModelResult = await rpc(
                            "/stock_barcode/get_specific_barcode_data",
                            updatedParams);
                        if('resticateMissingRecod' in notRestrictedByModelResult){
                            delete notRestrictedByModelResult['resticateMissingRecod']
                        }
                        this.setCache(notRestrictedByModelResult);
                    }
                }
            }
        }
        this.waitingFetch = [];
    },
    async _getMissingRecord(barcode, model, filters = {}) {
        const keyCache = JSON.stringify([...arguments]);
        const missCache = this.missingBarcodeKeyCache;
        const keyCacheWithoutModel = JSON.stringify([barcode, false, {}]);
        if (filters) {
            // If we already tried to find the same model's record for the given barcode but
            // without the filters, there is no need to try again with the filter.
            const keyCacheWithoutFilters = JSON.stringify([barcode, model, {}]);
            if (missCache.has(keyCacheWithoutFilters)) {
                return false;
            }
        }
        // Check if we already try to fetch this missing record.
        if (missCache.has(keyCache) || missCache.has(keyCacheWithoutModel)) {
            return false;
        }
        const params = {};
        if (model) {
            params.barcodes_by_model = { [model]: [barcode] };
        } else {
            params.barcode = barcode;
        }
        // Creates and passes a domain if some filters are provided.
        const domainsByModel = {};
        for (const filter of Object.entries(filters)) {
            const modelName = filter[0];
            const filtersByField = filter[1];
            domainsByModel[modelName] = [];
            for (const filterByField of Object.entries(filtersByField)) {
                if (filterByField[1] instanceof Array) {
                    domainsByModel[modelName].push([filterByField[0], 'in', filterByField[1]]);
                } else {
                    domainsByModel[modelName].push([filterByField[0], '=', filterByField[1]]);
                }
            }
        }
        params.domains_by_model = domainsByModel;
        const result = await rpc("/stock_barcode/get_specific_barcode_data", params);
         if('resticateMissingRecod' in result){
            delete result['resticateMissingRecod']
        }
        this.setCache(result);
        missCache.add(keyCache);
    },
})

patch(BarcodeModel.prototype, {
    async createNewProductLine(barcodeData) {
        const barcodes_by_model = { "product.product": [barcodeData.barcode] };
        const params = { barcodes_by_model };
        try {
            const result = await rpc("/stock_barcode/get_specific_barcode_data", params);
            if (Object.keys(result).length === 0) {
                const message = _t("No record found for the specified barcode");
                return this.notification(message, {
                    title: _t("Inconsistent Barcode"),
                    type: "danger",
                });
            }
            this.cache.setCache(result);

            // modifying the barcodeData
            const [productRecord] = result["product.product"];
            barcodeData.match = true;
            barcodeData.quantity = 1;
            barcodeData.product = productRecord;
            const fieldsParams = this._convertDataToFieldsParams(barcodeData);
            if (barcodeData.uom) {
                fieldsParams.uom = barcodeData.uom;
            }
            const currentLine = await this.createNewLine({fieldsParams});
            if (currentLine) {
                this._selectLine(currentLine);
            }
            this.trigger("update");
            return true;
        } catch (error) {
            return this.notification(error, {
                title: _t("RPC Error"),
                type: "danger",
            });
        }
    }
})
