/* @odoo-module */
import { _t } from "@web/core/l10n/translation";

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { EscPosPrinter } from "@lo_pos_tcp_escpos_printer/app/escpos_printer";
import { renderToElement, renderToString } from "@web/core/utils/render";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { renderToFragment } from "@web/core/utils/render";

patch(PosStore.prototype, {

    afterProcessServerData() {
        var self = this;
        return super.afterProcessServerData(...arguments).then(function () {
            if (self.config.escpos_print && self.config.escpos_printer_ip) {
                self.hardwareProxy.printer = new EscPosPrinter({
                    ip: self.config.escpos_printer_ip || false,
                    port: self.config.espos_printer_port || false,
                    order_receipt_type: 'all',
                    receipt_design: self.config.receipt_design && self.config.receipt_design.id || false,
                    receipt_design_text: self.config.receipt_design_text || false,
                    sticker_printer: self.config.sticker_printer || false,
                    escpos_print_cashdrawer: self.config.escpos_print_cashdrawer || false
                });
            }
        });
    },

    create_printer(config) {
        if (config.printer_type === "escpos_printer") {
            return new EscPosPrinter({ ip: config.escpos_printer_ip, port: config.espos_printer_port, order_receipt_type: config.order_receipt_type, receipt_design: config.receipt_design, receipt_design_text: config.receipt_design_text, sticker_printer: config.sticker_printer });
        } else {
            return super.create_printer(...arguments);
        }
    },

    async printChanges(order, orderChange) {
        const unsuccedPrints = [];
        const lastChangedLines = order.last_order_preparation_change.lines;
        orderChange.new.sort((a, b) => {
            const sequenceA = a.pos_categ_sequence;
            const sequenceB = b.pos_categ_sequence;
            if (sequenceA === 0 && sequenceB === 0) {
                return a.pos_categ_id - b.pos_categ_id;
            }
            return sequenceA - sequenceB;
        });

        for (const printer of this.unwatched.printers) {
            const changes = this._getPrintingCategoriesChanges(
                printer.config.product_categories_ids,
                orderChange
            );
            const toPrintArray = this.preparePrintingData(order, changes);
            const diningModeUpdate = orderChange.modeUpdate;
            if ((diningModeUpdate || !Object.keys(lastChangedLines).length) && changes.new.length > 0) {
                // Prepare orderlines based on the dining mode update
                const lines =
                    diningModeUpdate && Object.keys(lastChangedLines).length
                        ? lastChangedLines
                        : order.lines;

                // converting in format we need to show on xml
                const orderlines = Object.entries(lines).map(([key, value]) => ({
                    basic_name: diningModeUpdate ? value.basic_name : value.product_id.name,
                    isCombo: diningModeUpdate ? value.isCombo : value.combo_item_id?.id,
                    quantity: diningModeUpdate ? value.quantity : value.qty,
                    note: value.note,
                    sticker_note: value.sticker_note,
                    attribute_value_ids: value.attribute_value_ids,
                    product_id: value.product_id.id,
                    pos_prod_category_id: value.product_id.pos_categ_ids.map((line) => line.id),
                    total_price: value.price_unit ? value.price_unit : 0.0,
                    uuid: value.uuid,
                }));

                // ----------------
                // Filter lines based on changes (if applicable)
                const filteredOrderlines = [];
                orderlines.forEach((line) => {
                    const posCategIds = changes.new.map((change) => change.pos_categ_id);
                    if (posCategIds.includes(line.pos_prod_category_id[0])) {
                        filteredOrderlines.push(line);
                    }
                });
                //  -----------------------

                // Print detailed receipt
                const printed = await this.printReceipts(
                    order,
                    printer,
                    "New",
                    filteredOrderlines,
                    true,
                    diningModeUpdate
                );
                if (!printed) {
                    unsuccedPrints.push("Detailed Receipt");
                }
            } else {
                // Print all receipts related to line changes
                for (const [key, value] of Object.entries(toPrintArray)) {
                    const printed = await this.printReceipts(order, printer, key, value, false);
                    if (!printed) {
                        unsuccedPrints.push(key);
                    }
                }
                // Print Order Note if changed
                if (orderChange.generalNote) {
                    const printed = await this.printReceipts(order, printer, "Message", []);
                    if (!printed) {
                        unsuccedPrints.push("General Message");
                    }
                }
            }
        }

        // printing errors
        if (unsuccedPrints.length) {
            const failedReceipts = unsuccedPrints.join(", ");
            this.dialog.add(AlertDialog, {
                title: _t("Printing failed"),
                body: _t("Failed in printing %s changes of the order", failedReceipts),
            });
        }
    },

    async printReceipts(order, printer, title, lines, fullReceipt = false, diningModeUpdate) {
        let time;
        if (order.write_date) {
            time = order.write_date?.split(" ")[1].split(":");
            time = time[0] + "h" + time[1];
        }

        const printingChanges = {
            table_name: order.table_id ? order.table_id.table_number : "",
            config_name: order.config_id.name,
            time: order.write_date ? time : "",
            tracking_number: order.tracking_number,
            takeaway: order.config_id.takeaway && order.takeaway,
            employee_name: order.employee_id?.name || order.user_id?.name,
            order_note: order.general_note,
            diningModeUpdate: diningModeUpdate,
        };

        const orderReceiptType = printer.config.order_receipt_type;
        const customRecipt = []
        const customstickerdict = []
        if (! printer.sticker_printer) {
            if (orderReceiptType === "all") {
                if (printer.receipt_design && printer.receipt_design_text) {

                    // Make Custome Template
                    renderToString.app.addTemplate("lo_pos_tcp_escpos_printer.CustomDesignReceipt", printer.receipt_design_text);

                    const receipt = renderToElement("lo_pos_tcp_escpos_printer.CustomDesignReceipt", {
                        operational_title: title,
                        changes: printingChanges,
                        changedlines: lines,
                        fullReceipt: fullReceipt,
                    });
                    customRecipt.push(receipt)
                } else {
                    const receipt = renderToElement("point_of_sale.OrderChangeReceipt", {
                        operational_title: title,
                        changes: printingChanges,
                        changedlines: lines,
                        fullReceipt: fullReceipt,
                    });
                    customRecipt.push(receipt)
                }
            } else if (orderReceiptType === "menu_order_qty") {
                for (const line of lines) {
                    for (let i = 0; i < line.quantity; i++) {
                        const singleItemReceipt = [{ ...line, quantity: 1 }];
                        if (printer.receipt_design && printer.receipt_design_text) {

                            // Make Custome Template
                            renderToString.app.addTemplate("lo_pos_tcp_escpos_printer.CustomDesignReceipt", printer.receipt_design_text);

                                const receipt = renderToElement("lo_pos_tcp_escpos_printer.CustomDesignReceipt", {
                                operational_title: title,
                                changes: printingChanges,
                                changedlines: singleItemReceipt,
                                fullReceipt: fullReceipt,
                            });
                            customRecipt.push(receipt)
                        } else {
                            const receipt = renderToElement("point_of_sale.OrderChangeReceipt", {
                                operational_title: title,
                                changes: printingChanges,
                                changedlines: singleItemReceipt,
                                fullReceipt: fullReceipt,
                            });
                            customRecipt.push(receipt)
                        }
                    };
                };
            } else if (orderReceiptType === "menu_order_product") {
                for (const line of lines) {
                    const singleProductReceipt = [line];
                    if (printer.receipt_design && printer.receipt_design_text) {

                        // Make Custome Template
                        renderToString.app.addTemplate("lo_pos_tcp_escpos_printer.CustomDesignReceipt", printer.receipt_design_text);

                        const receipt = renderToElement("lo_pos_tcp_escpos_printer.CustomDesignReceipt", {
                            operational_title: title,
                            changes: printingChanges,
                            changedlines: singleProductReceipt,
                            fullReceipt: fullReceipt,
                        });
                        customRecipt.push(receipt)
                    } else {
                        const receipt = renderToElement("point_of_sale.OrderChangeReceipt", {
                            operational_title: title,
                            changes: printingChanges,
                            changedlines: singleProductReceipt,
                            fullReceipt: fullReceipt,
                        });
                        customRecipt.push(receipt)
                    }
                }
            }
            const result = await printer.printReceipt(customRecipt);
            return result.successful;
        } else {
            if (title != 'Cancel') {
                const orderLines = posmodel.get_order().lines;
                const matchedLines = [];

                lines.forEach(line => {
                    const match = orderLines.filter(orderLine => orderLine.uuid === line.uuid);
                    matchedLines.push(...match);
                });
                renderToString.app.addTemplate("lo_pos_tcp_escpos_printer.CustomDesignReceipt", printer.receipt_design_text);
                const receiptSticker = renderToFragment("lo_pos_tcp_escpos_printer.CustomDesignReceipt", {
                    changes: printingChanges,
                    changedlines: matchedLines,
                    order: order,
                });
                customstickerdict.push(receiptSticker.textContent)
            }
            const result = await printer.printReceipt(customstickerdict);
            return result.successful;
        }
    },
});