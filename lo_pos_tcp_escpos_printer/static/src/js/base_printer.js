/* @odoo-module */

import { BasePrinter } from "@point_of_sale/app/printer/base_printer";
import { htmlToCanvas } from "@point_of_sale/app/printer/render_service";
import { patch } from "@web/core/utils/patch";

patch(BasePrinter.prototype, {

    async printReceipt(receipt) {
        if (receipt) {
            this.receiptQueue.push(receipt);
        }
        // List to hold all receipt images
        let printResult;
        const images = [];
        // Process all receipts in the queue
        while (this.receiptQueue.length > 0) {
            const receiptBatch = this.receiptQueue.shift();
            if (!this.sticker_printer) {
                if (Array.isArray(receiptBatch)) {
                    for (let rcp of receiptBatch) {
                        let image_restaurant;
                        image_restaurant = this.processCanvas(
                            await htmlToCanvas(rcp, { addClass: "pos-receipt-print" })
                        );
                        images.push(image_restaurant);
                    }
                } else {
                    let images_order;
                    images_order = this.processCanvas(
                        await htmlToCanvas(receiptBatch, { addClass: "pos-receipt-print" })
                    );
                    images.push(images_order);
                }
            } else {
                if (Array.isArray(receiptBatch)) {
                    for (let rcp of receiptBatch) {
                        images.push(rcp);
                    }
                } else {
                    images.push(receiptBatch);
                }
            }
        }
        // Send all images in a single printing job
        try {
            const printResult = await this.sendPrintingJob(images); // Pass the list of images
            if (!printResult || printResult.result === false) {
                // Handle failed printing result
                this.receiptQueue.length = 0;
                return this.getResultsError(printResult);
            }
        } catch (error) {
            console.error("Error while sending print job:", error);
            // Handle communication error with the IoT box
            this.receiptQueue.length = 0;
            return this.getActionError();
        }
        return { successful: true }; // Return successful status if all prints succeed
    },

});