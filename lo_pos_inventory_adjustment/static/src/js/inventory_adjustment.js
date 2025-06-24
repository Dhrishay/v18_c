import { _t } from "@web/core/l10n/translation";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";
import { useRef, useState, Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { rpc } from "@web/core/network/rpc";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

export class InventoryLocationPopupWidget extends Component {
    static template = 'lo_pos_inventory_adjustment.InventoryLocationPopupWidget';
    static components = {
        Dialog,
    };
    static props = {
        ...Dialog.props,
        close: Function,
        title: String,
        slots: { type: Object, optional: true },
    };
    setup() {
        super.setup();
        this.pos = usePos();
        this.dialog = useService("dialog");
    }
    async confirm(ev) {
        var self = this
        var is_multi_location = this.pos.config.is_multi_location;
        var location_barcode = document.querySelector('#locataion')
        if(location_barcode){
            location_barcode = location_barcode.value
        }
        var pda = document.querySelector('#pda')
        if(pda){
            pda = pda.value
        }
        var warehouse = this.pos.config.warehouse_name;
        if (is_multi_location) {
            var result = await rpc("/check_location", { location_barcode: location_barcode });
            if(result){
                var stock_warehouse = document.querySelector('#stock-warehouse')
                var stock_loc = document.querySelector('#stock-loc')
                var stock_pda = document.querySelector('#stock-pda')

                if(!(location_barcode && pda)){
                    this.dialog.add(AlertDialog, {
                        title: _t("Warning"),
                        body: _t("You do not add Location or PDA")
                    });
                }else{
                    if(stock_warehouse){
                        stock_warehouse.innerHTML = warehouse;
                    }
                    if(stock_loc){
                        stock_loc.innerHTML = location_barcode;
                    }
                    if(stock_pda){
                        stock_pda.innerHTML = pda;
                    }
                    this.props.close();
                    var success_msg = 'Successfully Add Location'
                    this.dialog.add(ConfirmationDialog, {
                        title: _t('Confirmation'),
                        body: _t(success_msg),
                    });
                }

            }else{
                this.dialog.add(AlertDialog, {
                    title: _t("Warning"),
                    body: _t("Location is not Found")
                });
            }
        }else{
            var stock_warehouse = document.querySelector('#stock-warehouse')
            var stock_loc = document.querySelector('#stock-loc')
            var stock_pda = document.querySelector('#stock-pda')
            if(!(location_barcode && pda)){
                this.dialog.add(AlertDialog, {
                    title: _t("Warning"),
                    body: _t("You do not add Location or PDA")
                });
            }else{
                if(stock_warehouse){
                    stock_warehouse.innerHTML = warehouse;
                }
                if(stock_loc){
                    stock_loc.innerHTML = location_barcode;
                }
                if(stock_pda){
                    stock_pda.innerHTML = pda;
                }
                this.props.close();
                var success_msg = 'Successfully Add Location'
                this.dialog.add(ConfirmationDialog, {
                    title: _t('Confirmation'),
                    body: _t(success_msg),
                });
           }
        }
    }
    async cancel() {
        this.props.close();
    }
}

export class InventoryAdjustmentsPopupWidget extends Component {
    static template = 'lo_pos_inventory_adjustment.InventoryAdjustmentsPopupWidget';
    static components = {
        Dialog,
    };
    static props = {
        ...Dialog.props,
        close: Function,
        title: { type: String, optional: true },
        slots: { type: Object, optional: true },
        warehouse_no: { type: String, optional: true },
        location_no: { type: String, optional: true },
        pda: { type: String, optional: true },
        orderlines_length: { type: Number, optional: true },
    };
    setup() {
        super.setup();
        this.pos = usePos();
        this.dialog = useService("dialog");
    }
    async confirm(ev) {
        var stock_inventory = {};
        var header = [{warehouse_no:null,location_no:null,pda:null,pos_name:null,pos_config_id:null,employee_id:null}];
        header[0].warehouse_no = this.pos.config.warehouse_name;
        var stock_loc = document.querySelector('#stock-loc')
        var stock_pda = document.querySelector('#stock-pda')
        if(stock_loc){
            stock_loc = stock_loc.innerHTML;
            header[0].location_no = stock_loc;
        }
        if(stock_pda){
            stock_pda = stock_pda.innerHTML;
            header[0].pda = stock_pda;
        }
        header[0].pos_name = this.pos.config.name;
        header[0].pos_config_id = this.pos.config.id;
        header[0].employee_id = this.pos.get_cashier().id;

        var order_lines = this.pos.get_order().lines;
        stock_inventory.line_ids = [];
        for (var line in order_lines){
            var is_same_product_line = false
            for (var same_line in stock_inventory.line_ids){
                if(stock_inventory.line_ids[same_line][2].product_id == order_lines[line].product_id.id){
                    is_same_product_line = true
                    stock_inventory.line_ids[same_line][2].product_qty = stock_inventory.line_ids[same_line][2].product_qty + order_lines[line].qty
                }
            }
            if(!is_same_product_line){
                var stock_inventory_line = [0,false,{product_id:null,product_qty:0,theoretical_qty:0,product_uom_id:null,location_id:null}]
                stock_inventory_line[2].product_id = order_lines[line].product_id.id;
                stock_inventory_line[2].product_uom_id = order_lines[line].product_id.uom_id.id;
                stock_inventory_line[2].product_qty = order_lines[line].qty;
                stock_inventory_line[2].location_id = this.pos.config.adjst_location_id.id;
                stock_inventory.line_ids.push(stock_inventory_line);
            }
        }
        stock_inventory.from_pos = true;
        stock_inventory.location_ids = [(4, [this.pos.config.adjst_location_id.id])];
        var validate = false;
        let stock_inventory_reponse = await rpc("/create/inventory_from_pos", {header:header,orders:stock_inventory,validate:validate});

        if(stock_inventory_reponse){
            var error_msg = '';
            stock_inventory_reponse.forEach((msg) => {
                error_msg += msg + ' \n \n';
            });
            await this.dialog.add(AlertDialog, {
                title: _t("Warning"),
                body: _t(error_msg)
            });
        }
        else{
            const order_only = this.pos.get_order()
            const lineToDelete = [];
            await order_only.lines.forEach((line) => {
                lineToDelete.push(line);
            });
            for (const line of lineToDelete) {
                line.delete();
            }
            await this.pos.syncAllOrders()
            await this.props.close();
            var success_msg = 'Successfully generated inventory adjustment for selected products and quantities, please process it further!'
            this.dialog.add(ConfirmationDialog, {
                title: _t('Confirmation'),
                body: _t(success_msg),
            });
        }
    }
    async cancel() {
        this.props.close();
    }
}

patch(ControlButtons.prototype, {
    setup() {
        super.setup();
    },
    async clickAddHeader() {
        await this.dialog.add(InventoryLocationPopupWidget, {
            title: _t("Inventory Adjustments"),
        });
    },
    async clickAdjustInventory() {
        var warehouse_no = this.pos.config.warehouse_name;
        var location_no = document.querySelector('#stock-loc')
        var pda = document.querySelector('#stock-pda')
        if(location_no){
            location_no = location_no.innerHTML
        }
        if(pda){
            pda = pda.innerHTML
        }
        var order_lines = this.pos.get_order().lines;
        var orderlines_length = this.pos.get_order().lines.length;

        if(orderlines_length > 0 && location_no != ''){
            await this.dialog.add(InventoryAdjustmentsPopupWidget,{
                title : _t("Inventory Adjustments"),
                warehouse_no : warehouse_no,
                location_no : location_no,
                pda : pda,
                orderlines_length : orderlines_length,
            });
        }else if(orderlines_length == 0){
            await this.dialog.add(AlertDialog, {
                title: _t("Invalid Inventory Adjustment"),
                body: _t("Please add few product (s) for inventory adjustment")
            });
        }else if(location_no == ''){
            await this.dialog.add(AlertDialog, {
                title: _t("Invalid Inventory Adjustment"),
                body: _t("Please add Location")
            });
        }
    }
});
