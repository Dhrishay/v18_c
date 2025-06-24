import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, useRef, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class PopupPaymentWidget extends Component {
    static template = "bi_pos_reports.PopupPaymentWidget";
    static components = {
        Dialog,
    };
    static props = ["close"];

    setup() {
		super.setup();
		this.pos = usePos();
		this.orm = useService('orm');
		this.state = useState({ OrderStartDate: "", OrderEndDate: "", PaymentSummary: "" });
		
		onMounted(() =>{
			document.getElementById('dt_strt').setAttribute("style", "display: none ;");
			document.getElementById('dt_end').setAttribute("style", "display: none ;");
			
		});
	}
	go_back_screen() {
		this.pos.showScreen('ProductScreen');
		this.props.close();
	}

	clickCurrentSession(){
		if (document.getElementById('pymnt_crnt_ssn').checked) {
			document.getElementById('strt_dt').setAttribute("style", "display: none ;");
			document.getElementById('end_dt').setAttribute("style", "display: none ;");

		}
		else{
			document.getElementById('strt_dt').setAttribute("style", "display: block ;");
			document.getElementById('end_dt').setAttribute("style", "display: block ;");
		}
	}

	async render_payment_summary(){
		
		document.getElementById('dt_strt').setAttribute("style", "display: none ;");
		document.getElementById('dt_end').setAttribute("style", "display: none ;");
		
		var self = this;
		var is_current_session = document.getElementById('pymnt_crnt_ssn').checked
		var pay_st_date = this.state.OrderStartDate
		var pay_ed_date = this.state.OrderEndDate
		var smry_payment = this.state.PaymentSummary 

		var order = this.pos.get_order();
		var config_id = self.pos.config_id
		var curr_session = self.pos.config.current_session_id.id;
		var payment_summary = [];
		var cashier = this.pos.get_cashier();
		var cashier_id = this.pos.get_cashier_user_id();
		document.getElementById('dt_strt').setAttribute("style", "display: none ;");
		document.getElementById('dt_end').setAttribute("style", "display: none ;");

		if(is_current_session == true)	
		{
			await self.env.services.orm.call(
				'pos.report.payment', 
				'get_crnt_ssn_payment_pos_order', 
				[1,smry_payment,cashier.id,cashier_id,config_id,curr_session,is_current_session,pay_st_date,pay_ed_date], 
			).then(function(data){ 
				var payments = data[2];
				payment_summary = data[1];
				var final_total = data[0];
				
				self.props.close({ confirmed: false, payload: null });

				self.pos.showScreen('PaymentReceiptWidget',{
					payment_summary:payment_summary,
					final_total:final_total,
					is_current_session:is_current_session,
					payments : payments,
					smry_payment : smry_payment,
				});
				self.props.close()
			});
		}
		else{
			if(!pay_st_date){
				document.getElementById('dt_strt').setAttribute("style", "display: block ;");
				setTimeout(function() {document.getElementById('dt_strt').setAttribute("style", "display: none ;");},3000);
				return
			}
			else if(!pay_ed_date){
				document.getElementById('dt_end').setAttribute("style", "display: block ;");
				setTimeout(function() {document.getElementById('dt_end').setAttribute("style", "display: none ;");},3000);
				return
			}
			else{

				await self.env.services.orm.call(
					'pos.report.payment', 
					'get_crnt_ssn_payment_pos_order', 
					[1,smry_payment,cashier.id,cashier_id,config_id,curr_session,is_current_session,pay_st_date,pay_ed_date], 
				).then(function(data){ 
					var payments = data[2];
					payment_summary = data[1];
					var final_total = data[0];
					
					self.props.close({ confirmed: false, payload: null });
					self.pos.showScreen('PaymentReceiptWidget',{
						payment_summary:payment_summary,
						final_total:final_total,
						is_current_session:is_current_session,
						payments : payments,
						start_date_pay:pay_st_date,
						end_date_pay:pay_ed_date,
						smry_payment : smry_payment,
					});
				});
				self.props.close()
			}

		}
	}
}