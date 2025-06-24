/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { _t } from "@web/core/l10n/translation";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
patch(ControlButtons.prototype, {
    async clickRewards() {
        const rewards = this.getPotentialRewards();
        const { loyalty_id } = this.pos.config;
        // Return early if no rewards or no loyalty_id configuration.
        if (!rewards.length) return;
        if (loyalty_id){
    
        const rewardIds = loyalty_id.reward_ids.map(re => re.id);
    
        // Update relevant rewards based on loyalty program
        rewards.forEach(reward => {
            const { reward: rewardData } = reward;
            if (rewardData.program_id && rewardIds.includes(rewardData.id)) {
                rewardData.description = 'Confirm With Qr Code';
                rewardData.name = 'qr_code_name';
            }
        });
    
        const rewardsList = rewards.map(({ reward }) => ({
            id: reward.id,
            label: reward.program_id.name,
            description: `Add "${reward.description}"`,
            item: reward,
            name: reward.name,
        }));
    
        // Open dialog with the list of rewards
        this.dialog.add(SelectionPopup, {
            title: _t("Available rewards"),
            list: rewardsList,
            getPayload: (selectedReward) => {
                this._applyReward(
                    selectedReward.reward,
                    selectedReward.coupon_id,
                    selectedReward.potentialQty
                );
            },
        });
    }
    else{

        super.clickRewards();
    }
    }

});
