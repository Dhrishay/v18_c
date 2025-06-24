
import { patch } from "@web/core/utils/patch";
import { BarcodeObject } from '@stock_barcode/barcode_object';


patch(BarcodeObject.prototype, {
    async fetchProduct(productBarcode, options) {
        const packaging = await this.cache.getRecordByBarcode(productBarcode, "product.packaging", {
            fetchLater : true,
            onlyInCache: true
        });
        let product;
        if (packaging) {
            product = this.cache.getRecord("product.product", packaging.product_id, false);
            this.parsedData.packaging = packaging;
            this.parsedData.quantity = packaging.qty;
        }
        if (!product) {
             product = await this.cache.getRecordByBarcode(productBarcode, "product.product", options);
        }
        if (product) {
            this.parsedData.product = product;
        } else {
            this.missingRecords.push({ type: "product", productBarcode });
        }
    }
});