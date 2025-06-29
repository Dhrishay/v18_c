/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import {Component } from "@odoo/owl";

export class XMLPosOrderSummaryReceipt extends Component {
    static template = "bi_pos_reports.XMLPosOrderSummaryReceipt";
    
    setup() {
        this.pos = usePos();
        
    }
    get summery(){
		let categs = this.props.order;
		let summery = [];
		categs.forEach((categs) => {
			if(categs){
				summery.push(categs)
			}
		});
		return summery;
	}
}

