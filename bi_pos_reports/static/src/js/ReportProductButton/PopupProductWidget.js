import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, useRef, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Dialog } from "@web/core/dialog/dialog";

export class PopupProductWidget extends Component {
    static template = "bi_pos_reports.PopupProductWidget";
    static components = {
        Dialog,
    };
    static props = ["close"];

    setup() {
		super.setup();
		this.pos = usePos();
		this.orm = useService('orm');
		this.state = useState({ ProductStartDate: "", ProductEndDate: "" });
		onMounted(() =>{
			document.getElementById('prod_dt_strt').setAttribute("style", "display: none ;");
			document.getElementById('prod_dt_end').setAttribute("style", "display: none ;");
		});
	}
	go_back_screen() {
		this.props.close({ confirmed: false, payload: null });
	}
	clickCurrentSession(){
		if (document.getElementById('prod_crnt_ssn').checked) {
			document.getElementById('prod_st_dt').setAttribute("style", "display: none ;");
			document.getElementById('prod_end_dt').setAttribute("style", "display: none ;");
		}
		else{
			document.getElementById('prod_st_dt').setAttribute("style", "display: block ;");
			document.getElementById('prod_end_dt').setAttribute("style", "display: block ;");
		}
	}
		
	print_product(){
		var self = this;
		var pro_st_date = this.state.ProductStartDate
		var pro_ed_date = this.state.ProductEndDate
		var order = this.pos.get_order();
		var summery_product = [];
		var curr_session = self.pos.config.current_session_id.id;
		var prod_current_session = document.getElementById('prod_crnt_ssn').checked
		document.getElementById('prod_dt_strt').setAttribute("style", "display: none ;");
		document.getElementById('prod_dt_end').setAttribute("style", "display: none ;");

		if(prod_current_session == true)	
		{
			self.env.services.orm.call(
				'pos.order',
				'update_product_summery',
				[order.id, pro_st_date, pro_ed_date,prod_current_session,curr_session],
			)
			.then(function(output_summery_product){
				summery_product = output_summery_product;
				self.save_product_summery_details(output_summery_product, pro_st_date, pro_ed_date,prod_current_session);
			});
		}
		else{
			if(!pro_st_date){
				document.getElementById('prod_dt_strt').setAttribute("style", "display: block ;");
				setTimeout(function() {document.getElementById('prod_dt_strt').setAttribute("style", "display: none ;");},3000);
				return
			}
			else if(!pro_ed_date){
				document.getElementById('prod_dt_end').setAttribute("style", "display: block ;");
				setTimeout(function() {document.getElementById('prod_dt_end').setAttribute("style", "display: none ;");},3000);
				return
			}
			else{
				self.env.services.orm.call(
					'pos.order',
					'update_product_summery',
					[order.id, pro_st_date, pro_ed_date,prod_current_session,curr_session],
				)
				.then(function(output_summery_product){
					summery_product = output_summery_product;
					self.save_product_summery_details(output_summery_product, pro_st_date, pro_ed_date,prod_current_session);
				
				});
			}
		}
	}
	
	save_product_summery_details(output_summery_product, pro_st_date, pro_ed_date,prod_current_session){
		var self = this;
		this.props.close();
		self.pos.showScreen('ProductReceiptWidget',{output_summery_product:output_summery_product, pro_st_date:pro_st_date, pro_ed_date:pro_ed_date,prod_current_session:prod_current_session});
	}
    
}
