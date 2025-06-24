/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { onWillStart, useRef, onMounted } from "@odoo/owl";

import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { useService } from "@web/core/utils/hooks";

patch(ControlButtons.prototype, {
    setup() {
        super.setup(...arguments);

        this.controlRef = useRef('control_button_ref');
        this.orm = useService("orm");

        // Fetch button size and color configuration on component initialization
        onWillStart(async () => {
            this.buttonColorSize = await this.orm.call(
                "pos.control.size.color",
                "get_color_size",
                [],
                { config_id: this.pos.config.id }
            );
        });

        // Apply button styles after the DOM is mounted
        onMounted(() => {
            if (this.controlRef.el) {
                const buttons = this.controlRef.el.querySelectorAll('button');
                buttons.forEach(button => this.applyButtonStyles(button));
            }
        });
    },

    /**
     * Apply styles to a button based on the configuration.
     * @param {HTMLElement} button - The button element.
     */
    applyButtonStyles(button) {

        const buttonText = button.innerText.trim();
        //CREATE BUTTON NAME RECORD TO SHOW BUTTON NAME IN CONFIGURATION
        this.orm.call(
        "pos.action.button",
        "create_button_record",
        [],
        {
             button_name: buttonText
        }
        );
        if (this.buttonColorSize) {
            // Filter configuration for the button based on its name
            // Apply height, width
            button.style.height = `${this.buttonColorSize.button_height}px`;
            button.style.width = `${this.buttonColorSize.button_width}px`;
            if (this.buttonColorSize.color_lines){
               const matchedLine = this.buttonColorSize.color_lines.find(line => line.name === buttonText);
                //Apply color styles

                if (matchedLine) {
                    button.style.backgroundColor = matchedLine.color;
                }


            }

        }
    },
});