/** @odoo-module **/
import { renderToElement } from "@web/core/utils/render";
import { _t } from "@web/core/l10n/translation";
import { Chatter } from "@mail/chatter/web_portal/chatter";
//import { COMMANDS } from "@barcodes/barcode_handlers";v
//import BarcodeQuantModel from '@stock_barcode/models/barcode_quant_model';
//import GroupedLineComponent from '@stock_barcode/components/grouped_line';
//import LineComponent from '@stock_barcode/components/line';
//import PackageLineComponent from '@stock_barcode/components/package_line';
import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { useService, useBus } from "@web/core/utils/hooks";
//import { Mutex } from "@web/core/utils/concurrency";
//import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { View } from "@web/views/view";
import { BarcodeVideoScanner, isBarcodeScannerSupported } from '@web/core/barcode/barcode_video_scanner';
import { url } from '@web/core/utils/urls';
import { utils as uiUtils } from "@web/core/ui/ui_service";
import { Component, EventBus, onPatched, onWillStart, onWillUnmount, useState, useSubEnv, useRef, onMounted } from "@odoo/owl";
import { ImportBlockUI } from "@base_import/import_block_ui";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";
//import { BarcodeInput } from "./manual_barcode";
//import { CountScreenRFID } from "./count_screen_rfid";

/** @odoo-module **/

import MainComponent from '@stock_barcode/components/main';
import { patch } from "@web/core/utils/patch";
import BarcodePickingModel from '@stock_barcode/models/barcode_picking_model';

patch(BarcodePickingModel.prototype, {
     get displayAddProductButton() {
        if(this.record.state == 'in_progress'){
            return false;
        }
        else if(this.record.picking_type_code == 'internal'){
            return !this._useReservation || this.config.barcode_allow_extra_product;
        }
        return false;
    }
});

const bus = new EventBus();

/**
 * Barcode Scan Location & Product Component
 */

class BarcodeMainComponent extends Component {
    static props = { ...standardActionServiceProps };
    static template = "lod_check_pro_loc_dc.BarcodeMainComponent";
    static components = {
        BarcodeVideoScanner,
        ImportBlockUI,
        View
    }

    //--------------------------------------------------------------------------
    // Lifecycle
    //--------------------------------------------------------------------------

    setup() {
        this.orm = useService('orm');
        this.notification = useService('notification');
        this.dialog = useService('dialog');
        this.action = useService('action');
        this.barcodeManual = useRef('manualBarcodeScannerInput');
        this.resModel = this.props.action.res_model;
        this.resId = this.props.action.context.active_id || false;
        this.state = useState({
            cameraScannedEnabled: false,
            view: 'barcodeLines',
            displayNote: false,
            displayCountRFID: false,
            uiBlocked: false,
            barcodesProcessed: 0,
            barcodesToProcess: 0,
            readyToToggleCamera: true,
        });
        this.bufferedBarcodes = [];
        this.receivedRFIDs = [];
        this.totalRFIDs = [];
        this.bufferingTimeout = null;
        this.barcodeService = useService("barcode");
        useBus(this.barcodeService.bus, "barcode_scanned", (ev) =>
            this.renderSearchLine(ev.detail.barcode)
        );
        this.mobileService = useService("mobile");
        useBus(this.mobileService.bus, "mobile_reader_scanned", (ev) =>
            this.onMobileReaderScanned(ev.detail.data)
        );

        onWillStart(() => this.onWillStart());

        onWillUnmount(() => {
            clearTimeout(this.bufferingTimeout);
        });

//      Autofocus processing was blocked because a document already has a focused element.
        onMounted(() => {
            this.barcodeManual.el.focus();
        });
    }

    onMobileReaderScanned(data) {
       this.receivedRFIDs.push(...data);
        this.totalRFIDs.push(...data);
        this.state.displayCountRFID = true;
        if (this.RFIDCountTimeout) {
            clearTimeout(this.RFIDCountTimeout);
        }
        this.RFIDCountTimeout = setTimeout(() => this.closeRFIDCount(), 5000);
        if (!this.bufferingTimeout) {
            this.bufferingTimeout = setTimeout(
                this._onMobileReaderScanned.bind(this),
                this.config.barcode_rfid_batch_time
            );
        }
        this.bufferedBarcodes = this.bufferedBarcodes.concat(data);
    }

    async _onMobileReaderScanned(ev) {
        await this.renderSearchLine(this.bufferedBarcodes.join(","))
        this.bufferedBarcodes = [];
        clearTimeout(this.bufferingTimeout);
        this.bufferingTimeout = null;
    }

    closeRFIDCount() {
        if (this.RFIDCountTimeout) {
            clearTimeout(this.RFIDCountTimeout);
        }
        this.state.displayCountRFID = false;
        this.receivedRFIDs = [];
    }

    async exit(ev) {
        this.state.cameraScannedEnabled = false;
        this.action.doAction('stock_barcode.stock_barcode_action_main_menu');
    }

    async applyBtnClick(ev){
        var barcode =   this.barcodeManual.el.value.trim()
        this.barcodeManual.el.value = "";
        this.renderSearchLine(barcode);

    }

    async _barcodeSearchOnKeydown(ev){
        if (ev.key === "Enter") {
            var barcode = this.barcodeManual.el.value.trim()
            this.barcodeManual.el.value = "";
            this.renderSearchLine(barcode)
        }
    }

    async renderSearchLine(barcode){
        if (barcode) {
            const barcodeData = await rpc("/check_location_and_product",{barcode: barcode});
            await this.changeView("barcodeLines");
            var template = "";
            if(barcodeData.is_location){
                template = "lod_check_pro_loc_dc.location_line_of_content";
            }
            else if(barcodeData.is_product){
                template = "lod_check_pro_loc_dc.product_line_of_content";
            }else{
                template = "lod_check_pro_loc_dc.empty_line_of_content";
            }
            const formReadonlyContent = await renderToElement(
                template, {
                    barcodeData: barcodeData,
                    barcode: barcode,
               }
            );
            const rederSection = document.getElementById('renderLineOfContent');
            rederSection.replaceChildren(formReadonlyContent);
            await this.playSound('success')
        } else {
            const message = _t("Please, Scan again!");
            this.env.services.notification.add(message, { type: 'warning' });
            await this.playSound('error')

        }
    }

    changeView(view) {
        this.state.cameraScannedEnabled = false;
        this.state.view = view;
    }

    setupCameraScanner() {
        this.cameraScannerSupported = isBarcodeScannerSupported();
        this.barcodeVideoScannerProps = {
            delayBetweenScan: this.config.delay_between_scan || 2000,
            facingMode: "environment",
            onResult: (barcode) => this.renderSearchLine(barcode),
            onError: (error) => {
                this.state.cameraScannedEnabled = false;
                const message = error.message;
                this.notification.add(message, { type: 'warning' });
            },
            onReady: () => {
                this.state.readyToToggleCamera = true;
            },
            cssClass: "o_stock_barcode_camera_video",
        };
    }

    async onWillStart() {
        const barcodeData = await rpc("/stock_barcode/get_barcode_data", {
            model: this.resModel,
            res_id: this.resId,
        });
        barcodeData.actionId = this.props.actionId;
        this.config = { play_sound: true, ...barcodeData.data.config };
        if (this.config.play_sound) {
            const fileExtension = new Audio().canPlayType("audio/ogg") ? "ogg" : "mp3";
            this.sounds = {
                error: new Audio(url(`/barcodes/static/src/audio/error.${fileExtension}`)),
                notify: new Audio(url(`/mail/static/src/audio/ting.${fileExtension}`)),
                success: new Audio(url(`/stock_barcode/static/src/audio/success.${fileExtension}`)),
            };
            this.sounds.error.load();
            this.sounds.notify.load();
            this.sounds.success.load();
        }
        this.setupCameraScanner();
    }

    playSound(soundType) {
        if (!this.config.play_sound) {
            return;
        }
        const type = soundType || "notify";
        this.sounds[type].currentTime = 0;
        this.sounds[type].play().catch((error) => {
            // `play` returns a promise. In case this promise is rejected (permission
            // issue for example), catch it to avoid Odoo's `UncaughtPromiseError`.
            console.log(error);
        });
    }


    // UI Methods --------------------------------------------------------------
    addBarcodesCountToProcess(count) {
        this.state.barcodesToProcess += count;
        if (this.state.barcodesToProcess > this.state.barcodesProcessed) {
            this.updateBarcodesCountMessage();
            this.blockUI();
        }
    }

    updateBarcodesCountProcessed() {
        this.state.barcodesProcessed++;
        this.updateBarcodesCountMessage();
        if (this.state.barcodesProcessed >= this.state.barcodesToProcess) {
            this.clearBarcodesCountProcessed();
        }
    }

    clearBarcodesCountProcessed() {
        this.state.barcodesProcessed = 0;
        this.state.barcodesToProcess = 0;
        this.unblockUI();
    }

    updateBarcodesCountMessage() {
        this.blockUIMessage = _t("Processing %(processed)s/%(toProcess)s barcodes", {
            processed: this.state.barcodesProcessed,
            toProcess: this.state.barcodesToProcess,
        });
    }

    blockUI(ev) {
        this.state.uiBlocked = true;
    }

    unblockUI() {
        this.state.uiBlocked = false;
        this.render(true);
    }


    //--------------------------------------------------------------------------
    // Camera scanner
    //--------------------------------------------------------------------------

    toggleCameraScanner() {
        if (!this.state.cameraScannedEnabled) {
            this.state.cameraScannedEnabled = true;
            this.state.readyToToggleCamera = false;
        } else if (this.state.readyToToggleCamera) {
            this.state.cameraScannedEnabled = false;
        }
    }

    get cameraScannerClassState() {
        if (!this.state.readyToToggleCamera) {
            return "bg-secondary";
        }
        return this.state.cameraScannedEnabled ? "bg-success text-white" : "text-primary";
    }

    _getHeaderHeight() {
        const header = document.querySelector('.o_barcode_header');
        const navbar = document.querySelector('.o_main_navbar');
        // Computes the real header's height (the navbar is present if the page was refreshed).
        return navbar ? navbar.offsetHeight + header.offsetHeight : header.offsetHeight;
    }
}

registry.category("actions").add("stock_barcode_check_product_and_location_action", BarcodeMainComponent);

export default BarcodeMainComponent;
