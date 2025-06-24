import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, useRef, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Dialog } from "@web/core/dialog/dialog";

export class PopupCategoryWidget extends Component {
    static template = "bi_pos_reports.PopupCategoryWidget";
    static components = {
        Dialog,
    };

    setup() {
		super.setup();
		this.pos = usePos();
		this.orm = useService('orm');
		this.state = useState({ CategoryStartDate: "", CategoryEndDate: "" });
		onMounted(() =>{
			document.getElementById('categ_dt_strt').setAttribute("style", "display: none ;");
			document.getElementById('categ_dt_end').setAttribute("style", "display: none ;");
		});
	}

	static props = ["close"];

	back() {
		this.props.close();
	}

	clickCurrentSession(){
		if (document.getElementById('categ_crnt_ssn').checked) {
			document.getElementById('ct_st_dt').setAttribute("style", "display: none ;");
			document.getElementById('ct_end_dt').setAttribute("style", "display: none ;");
		}
		else{
			document.getElementById('ct_st_dt').setAttribute("style", "display: block ;");
			document.getElementById('ct_end_dt').setAttribute("style", "display: block ;");
		}
	}

	async print_category_summary(){
		var self = this;
		var categ_st_date = this.state.CategoryStartDate
		var categ_ed_date = this.state.CategoryEndDate
		var category_summary = [];
		var current_lang = self.context
		var curr_session = self.pos.config.current_session_id.id;
		var categ_current_session = document.getElementById('categ_crnt_ssn').checked
		document.getElementById('categ_dt_strt').setAttribute("style", "display: none ;");
		document.getElementById('categ_dt_end').setAttribute("style", "display: none ;");

		if(categ_current_session == true)	
		{
			await self.env.services.orm.call(
				'pos.report.category', 
				'get_category_pos_order', 
				[self.pos.order_sequence,categ_st_date,categ_ed_date,curr_session,categ_current_session], 
			).then(function(data){ 
				category_summary = data;
				var make_total = [];
				var final_total = null;

				for(var i=0;i<category_summary.length;i++){
					make_total.push(category_summary[i].sum)
					final_total = make_total.reduce(function(acc, val) { return acc + val; });
				}
				self.props.close({ confirmed: false, payload: null });
				self.pos.showScreen('CategoryReceiptWidget',{
					category_summary:category_summary,
					start_date_categ:categ_st_date,
					end_date_categ:categ_ed_date,
					final_total:final_total,
					categ_current_session:categ_current_session,
				});
			});
		}
		else{
			if(categ_st_date == false){
				document.getElementById('categ_dt_strt').setAttribute("style", "display: block ;");
				setTimeout(function() {document.getElementById('categ_dt_strt').setAttribute("style", "display: none ;");},3000);
				return
			}
			else if(categ_ed_date == false){
				document.getElementById('categ_dt_end').setAttribute("style", "display: none ;");
				$('#categ_dt_end').show()
				setTimeout(function() {document.getElementById('categ_dt_end').setAttribute("style", "display: none ;");},3000);
				return
			}
			else{
				await self.env.services.orm.call(
					'pos.report.category', 
					'get_category_pos_order', 
					[self.pos.order_sequence,categ_st_date,categ_ed_date,curr_session,categ_current_session], 
				).then(function(data){ 
					category_summary = data;
					var make_total = [];
					var final_total = null;

					for(var i=0;i<category_summary.length;i++){
						make_total.push(category_summary[i].sum)
						final_total = make_total.reduce(function(acc, val) { return acc + val; });
					}
					self.props.close({ confirmed: false, payload: null });
					self.pos.showScreen('CategoryReceiptWidget',{
						category_summary:category_summary,
						start_date_categ:categ_st_date,
						end_date_categ:categ_ed_date,
						final_total:final_total,
						categ_current_session:categ_current_session,
					});
				});
			}
		}
	}

}
