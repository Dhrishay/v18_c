import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";

patch(ProductScreen.prototype, {
    setup() {
        super.setup(...arguments);
    },
    toogleNumpad(ev) {
        var num_pad = ev.target.parentElement.nextElementSibling;
        var arrow = ev.target;
        if(num_pad.classList.contains('pads') && !num_pad.classList.contains('d-none')){
            num_pad.classList.add('d-none');
            if(arrow.classList.contains('fa-caret-down')){
                arrow.classList.remove('fa-caret-down');
                arrow.classList.add('fa-caret-up');
            }
        }else if(num_pad.classList.contains('pads') && num_pad.classList.contains('d-none')){
            num_pad.classList.remove('d-none');
            if(arrow.classList.contains('fa-caret-up')){
                arrow.classList.remove('fa-caret-up');
                arrow.classList.add('fa-caret-down');
            }
        }
    }
});

