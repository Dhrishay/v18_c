/** @odoo-module */

import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { changesToOrderSticker } from "@lo_pos_tcp_escpos_printer/sticker_note_button/print_sticker";
import { OrderlineNoteButton } from "@point_of_sale/app/screens/product_screen/control_buttons/customer_note_button/customer_note_button";

patch(PosOrderline.prototype, {
    setup() {
        super.setup(...arguments);
        this.sticker_note = this.get_sticker_note() || "";
    },

    set_sticker_note(sticker_note){
        this.sticker_note = sticker_note;
    },

    get_sticker_note(){
        return this.sticker_note;
    },

    getDisplayData() {
        return {
            ...super.getDisplayData(),
            sticker_note: this.get_sticker_note() || "",
        };
    },

});

patch(Orderline, {
    props: {
        ...Orderline.props,
        line: {
            ...Orderline.props.line,
            shape: {
                ...Orderline.props.line.shape,
                sticker_note: { type: [Object,String], optional: true },
            },
        },
    },
});

patch(ControlButtons.prototype, {

    async onClickStickerNote(){
        const selectedOrderline = this.pos.get_order().get_selected_orderline();
        const selectedNote = selectedOrderline.sticker_note || "";
        const oldNote = selectedOrderline.get_sticker_note();
        const payload = await this.openStickerTextInput(selectedNote);

        var quantity_with_note = 0;
        const changes = this.pos.getOrderChanges();
        for (const key in changes.orderlines) {
            if (changes.orderlines[key].uuid == selectedOrderline.uuid) {
                quantity_with_note = changes.orderlines[key].quantity;
                break;
            }
        }
        const saved_quantity = selectedOrderline.qty - quantity_with_note;
        if (saved_quantity > 0 && quantity_with_note > 0) {
            await this.pos.addLineToCurrentOrder({
                product_id: selectedOrderline.product_id,
                qty: quantity_with_note,
                sticker_note: payload,
            });
            selectedOrderline.qty = saved_quantity;
        } else {
            selectedOrderline.sticker_note = payload;
        }

        return { confirmed: typeof payload === "string", inputNote: payload, oldNote };
    },

    async openStickerTextInput(selectedNote) {
        let buttons = [];

        buttons = this.pos.models["pos.note"].getAll().filter((note) => note.sticker_note == true).map((note) => ({
            label: note.name,
            isSelected: selectedNote.split("\n").includes(note.name), // Check if the note is already selected
        }));
        
        return await makeAwaitable(this.dialog, TextInputPopup, {
            title: _t("Add Sticker Note"),
//            title: _t("Add %s", this.props.label),
            buttons,
            rows: 4,
            startingValue: selectedNote,
        });
    },

    async clickPrintSticker() {
        await this.pos.printStickerNote(this.currentOrder);
        
    }

});

patch(PosStore.prototype, {
    async addLineToCurrentOrder(vals, opts = {}, configure = true) {
        await super.addLineToCurrentOrder(vals, opts,configure);
        if(this.get_order().get_selected_orderline()){
            this.get_order().get_selected_orderline().set_sticker_note();
        }
    },

     // Now the printer should work in PoS without restaurant
     async printStickerNote(order, cancelled = false) {
        if (this.printers_category_ids_set.size) {
            try {
                const orderChange = changesToOrderSticker(
                    order,
                    false,
                    this.orderPreparationCategories,
                    cancelled
                ); 
                this.printChanges(order, orderChange);
            } catch (e) {
                console.info("Failed in printing the changes in the order", e);
            }
        }
    },

    getReceiptHeaderData(order) {
        const result = super.getReceiptHeaderData(...arguments); 
        result.cashier = _t("%s", order?.getCashierName() || this.get_cashier()?.name)
        result.session_id = order.session_id.name
        return result;
    },
    
});

patch(PosOrder.prototype, {

    updateLastOrderChange() {
        const orderlineIdx = [];
        this.lines.forEach((line) => {
            if (!line.skip_change) {
                orderlineIdx.push(line.preparationKey);
    
                if (this.last_order_preparation_change.lines[line.preparationKey]) {
                    this.last_order_preparation_change.lines[line.preparationKey]["quantity"] =
                        line.get_quantity();
                    this.last_order_preparation_change.lines[line.preparationKey]["note"] =
                        line.getNote();
                    this.last_order_preparation_change.lines[line.preparationKey]["stciker_note"] =
                        line.get_sticker_note();
                } else {
                    this.last_order_preparation_change.lines[line.preparationKey] = {
                        attribute_value_ids: line.attribute_value_ids.map((a) => ({
                            ...a.serialize({ orm: true }),
                            name: a.name,
                        })),
                        uuid: line.uuid,
                        isCombo: line.combo_item_id?.id,
                        product_id: line.get_product().id,
                        name: line.get_full_product_name(),
                        basic_name: line.get_product().name,
                        display_name: line.get_product().name,
                        note: line.getNote(),
                        sticker_note: line.get_sticker_note(),
                        quantity: line.get_quantity(),
                        full_product_name: line.get_full_product_name(),
                        symbol: line.order_id.company_id.currency_id ? line.order_id.company_id.currency_id.name : 'LAK',
                        total_price: line.price_unit ? line.price_unit : 0.0,
                    };
                }

                line.setHasChange(false);
                line.saved_quantity = line.get_quantity();
            }
            
        });
    
        // Checks whether an orderline has been deleted from the order since it
        // was last sent to the preparation tools or updated. If so we delete older changes.
        for (const [key, change] of Object.entries(this.last_order_preparation_change.lines)) {
            const orderline = this.models["pos.order.line"].getBy("uuid", change.uuid);
            const lineNote = orderline?.note;
            const changeNote = change?.note;
            if (!orderline || (lineNote && changeNote && changeNote.trim() !== lineNote.trim())) {
                delete this.last_order_preparation_change.lines[key];
            }
        }
        this.last_order_preparation_change.sittingMode = this.takeaway ? "takeaway" : "dine in";
        this.last_order_preparation_change.generalNote = this.general_note;
    }
});

patch(OrderlineNoteButton.prototype, {
    async openTextInput(selectedNote) {
        let buttons = [];
        if (this._isInternalNote() || this.props.label == _t("General Note")) {
            buttons = this.pos.models["pos.note"].getAll().filter((note) => !note.sticker_note).map((note) => ({
                label: note.name,
                isSelected: selectedNote.split("\n").includes(note.name), // Check if the note is already selected
            }));
        }
        return await makeAwaitable(this.dialog, TextInputPopup, {
            title: _t("Add %s", this.props.label),
            buttons,
            rows: 4,
            startingValue: selectedNote,
        });
    }
})