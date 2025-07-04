/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import {Component } from "@odoo/owl";

export class XMLPosCategorySummaryReceipt extends Component {
    static template = "bi_pos_reports.XMLPosCategorySummaryReceipt";
    setup() {
        this.pos = usePos();
        
    }
    get cate_summary(){
		let categs = this.props.order.cate_summary;
		let cate_summary = [];
		categs.forEach((x) => {
			if(x){
				cate_summary.push(x)
			}
		});
		return cate_summary;
	}
}
