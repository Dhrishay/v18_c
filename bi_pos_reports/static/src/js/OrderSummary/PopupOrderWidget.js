import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, useRef, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Dialog } from "@web/core/dialog/dialog";

export class PopupOrderWidget extends Component {
    static template = "bi_pos_reports.PopupOrderWidget";
    static components = {
        Dialog,
    };
    static props = ["close"];
   
    setup() {
		super.setup();
		this.pos = usePos();
		this.orm = useService('orm');
		this.state = useState({ OrderStartDate: "", OrderEndDate: "", OrderState: "" });
		onMounted(() =>{
			document.getElementById('ordr_dt_strt').setAttribute("style", "display: none ;");
			document.getElementById('ordr_dt_end').setAttribute("style", "display: none ;");
			
		});
	}

	go_back_screen() {
		this.props.close();
	}
	clickCurrentSession(){
		if (document.getElementById('ordr_crnt_ssn').checked) {
			document.getElementById('order_st').setAttribute("style", "display: none ;");
			document.getElementById('order_end').setAttribute("style", "display: none ;");
		}
		else{
			document.getElementById('order_st').setAttribute("style", "display: block ;");
			document.getElementById('order_end').setAttribute("style", "display: block ;");
		}
	}
		
	async print_order (){
		var self = this;
		var ord_st_date = this.state.OrderStartDate
		var ord_end_date = this.state.OrderEndDate
		var ord_state = this.state.OrderState
		var order = self.pos.get_order();
		var summery_order = [];
		var curr_session = self.pos.config.current_session_id.id;
		var order_current_session = document.getElementById('ordr_crnt_ssn').checked
		document.getElementById('ordr_dt_strt').setAttribute("style", "display: none ;");
		document.getElementById('ordr_dt_end').setAttribute("style", "display: none ;");
		if(order_current_session == true)	
		{
			await self.env.services.orm.call(
					'pos.order',
					'update_order_summery',
					[order.sequence_number, ord_st_date, ord_end_date, ord_state,curr_session,order_current_session],
			).then(function(output_summery){
				summery_order = output_summery;
				self.save_summery_details(output_summery, ord_st_date, ord_end_date,order_current_session);
			
			});
		}
		else{
			if(ord_st_date == false){
				document.getElementById('ordr_dt_strt').setAttribute("style", "display: block ;");
				setTimeout(function() {document.getElementById('ordr_dt_strt').setAttribute("style", "display: none ;");},3000);
				return
			}
			else if(ord_end_date == false){
				document.getElementById('ordr_dt_end').setAttribute("style", "display: block ;");
				setTimeout(function() {document.getElementById('ordr_dt_end').setAttribute("style", "display: block ;");},3000);
				return
			}
			else{
				await self.env.services.orm.call(
					'pos.order',
					'update_order_summery',
					[order['sequence_number'], ord_st_date, ord_end_date,ord_state,curr_session,order_current_session],
				).then(function(output_summery){
					summery_order = output_summery;
					self.save_summery_details(output_summery, ord_st_date, ord_end_date,order_current_session);
				
				});
			}
		}
		
	}

	save_summery_details(output_summery, ord_st_date, ord_end_date,order_current_session){
		var self = this;
		self.pos.showScreen('OrderReceiptWidget',{output_summery:output_summery, ord_start_dt:ord_st_date, ord_end_dt:ord_end_date,order_current_session:order_current_session});
		this.props.close()
	}
    
}