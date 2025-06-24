import { _t } from "@web/core/l10n/translation";
import { Component, onMounted, useRef, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";

export class PopupLocationWidget extends Component {
    static template = "bi_pos_reports.PopupLocationWidget";
    static components = {
        Dialog,
    };
    static props = ["close","sessions"];
   	
   	setup() {
		super.setup();
		this.pos = usePos();
		this.orm = useService("orm");
		this.state = useState({ SelectedSession: "", SelectedLocation: "" });
		onMounted(() =>{
			document.getElementById('select_ssn').setAttribute("style", "display: none ;");
			document.getElementById('select_loc').setAttribute("style", "display: none ;");
		});
	}

	go_back_screen() {
		this.props.close();

	}

	get pos_sessions(){
		let sessions = this.props.sessions;
		let pos_sessions = [];
		sessions.forEach((session) => {
			if(session){
				pos_sessions.push(session)
			}
		});
		return pos_sessions;
	}

	get locations(){
		let pos_locations = this.pos.models['stock.location'].getAll();
		let locations = [];

		pos_locations.forEach((loc) => {
			if(loc){
				locations.push(loc)
			}
		});
		return locations;
	}
		
	async print_location(){
		var self = this;
		var select_session = this.state.SelectedSession; //$('.select_session_id').val();
		var location = this.state.SelectedLocation;     //$('.summery_location_id').val();
		var order = self.pos.get_order();
		var summery_product = [];
		var tab1 = document.getElementById('tab1').checked
		var tab2 = document.getElementById('tab2').checked
		document.getElementById('select_ssn').setAttribute("style", "display: none ;");
		document.getElementById('select_loc').setAttribute("style", "display: none ;");
		var should_print = false;
		if(tab1 == true)
		{
			should_print = true;
			if(select_session){
				await self.env.services.orm.call(
					'pos.order.location',
					'update_location_summery',
					[location, location,select_session,tab1,tab2],
				).then(function(output_summery_location){
					var summery_loc = output_summery_location;
					self.save_location_summery_details(output_summery_location,should_print);
				});
			}
			else{
				document.getElementById('select_ssn').setAttribute("style", "display: block ;");
				setTimeout(function() {document.getElementById('select_ssn').setAttribute("style", "display: none ;");},3000);
		// 		$('#tab1').prop('checked', true);
			}
		}
		else{
			if(location){
				await self.orm.call(
					'pos.order.location',
					'update_location_summery',
					[location, location,select_session,tab1,tab2],
				).then(function(output_summery_location){
					var summery_loc = output_summery_location;
					self.save_location_summery_details(output_summery_location,should_print);
				
				});
			}
			else{
				document.getElementById('select_loc').setAttribute("style", "display: block ;");;
				setTimeout(function() {document.getElementById('select_loc').setAttribute("style", "display: none ;");},3000);
				// $('#tab2').prop('checked', true);
			}
		}
	}
	
	save_location_summery_details(output_summery_location,should_print){
		var self = this;
		this.props.close({ confirmed: false, payload: null });
		self.pos.showScreen('LocationReceiptScreen',{output_summery_location:output_summery_location,ssn:should_print});
	}

}