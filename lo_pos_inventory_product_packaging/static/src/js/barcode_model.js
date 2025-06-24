import BarcodeModel from '@stock_barcode/models/barcode_model';
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(BarcodeModel.prototype, {
    async _fetchRecordFromTheCache(barcode, filters, data) {
        const result = data || { barcode, match: false };
        let recordByData = await this.cache.getRecordByBarcode(barcode, false, { filters });
        if (recordByData.size < 1 && 'product.barcode.multi' in this.cache.dbIdCache) {
            let barcode_ids = Object.values(this.cache.dbIdCache['product.barcode.multi'])
            if(barcode_ids && barcode_ids.length > 0){
                let barcode_obj = Object.values(this.cache.dbIdCache['product.barcode.multi']).find((rec)=> rec.name == barcode)
                let product;
                if(barcode_obj != undefined){
                    let product_id = barcode_obj.product_id
                    product = this.cache.getRecord("product.product", product_id, false);
                    if(product && Object.values(product).length > 0){
                        recordByData.set('product.product', JSON.parse(JSON.stringify(product)));
                    }
                }
            }
        }
        if (recordByData.size > 1) {
            if(recordByData.has('product.product') && recordByData.get('product.product') && !recordByData.get('product.product').is_pack_product){
                const message = _t(
                    "Barcode scan is ambiguous with several model: %s. Use the most likely.",
                    Array.from(recordByData.keys())
                );
                this.notification(message, { type: "warning" });
            }
        }

        if (this.groups.group_stock_multi_locations) {
            const location = recordByData.get('stock.location');
            if (location) {
                this._setLocationFromBarcode(result, location);
                result.match = true;
            }
        }

        if (this.groups.group_tracking_lot) {
            const packageType = recordByData.get('stock.package.type');
            const stockPackage = recordByData.get('stock.quant.package');
            if (stockPackage) {
                // TODO: should take packages only in current (sub)location.
                result.package = stockPackage;
                result.match = true;
            }
            if (packageType) {
                result.packageType = packageType;
                result.match = true;
            }
        }

        const product = recordByData.get('product.product');
        if (product) {
            result.product = product;
            result.match = true;
        }
        if (this.groups.group_stock_packaging) {
            const packaging = recordByData.get('product.packaging');
            if (packaging) {
                result.match = true;
                result.packaging = packaging;
            }
        }
        if (this.useExistingLots) {
            const lot = recordByData.get('stock.lot');
            if (lot) {
                result.lot = lot;
                result.match = true;
            }
        }

        if (!result.match && this.packageTypes.length) {
            // If no match, check if the barcode begins with a package type's barcode.
            for (const [packageTypeBarcode, packageTypeId] of this.packageTypes) {
                if (barcode.indexOf(packageTypeBarcode) === 0) {
                    result.packageType = await this.cache.getRecord('stock.package.type', packageTypeId);
                    result.packageName = barcode;
                    result.match = true;
                    break;
                }
            }
        }
        return result;
    }
});
