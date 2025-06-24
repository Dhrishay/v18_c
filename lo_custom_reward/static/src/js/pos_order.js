import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { browser } from "@web/core/browser/browser";
const { DateTime } = luxon;

patch(PosOrder.prototype, {

    getCustomerDisplayData() {
        return {
            ...super.getCustomerDisplayData(),
            qr_code: this.qr_code,
        };
    },

    _programIsApplicable(program) {
        
        if (
            program.trigger === "auto" &&
            !program.rule_ids.find(
                (rule) =>
                    rule.mode === "auto" || this.uiState.codeActivatedProgramRules.includes(rule.id)
            )
        ) {
            return false;
        }
        if (
            program.trigger === "with_code" &&
            !program.rule_ids.find((rule) =>
                this.uiState.codeActivatedProgramRules.includes(rule.id)
            )
        ) {
            return false;
        }

        if (program.is_nominative && !this.get_partner()) {
            return false;
        }
        
        if (program.date_from && program.date_from > DateTime.now()) {
            return false;
        }
        if (program.date_to && program.date_to < DateTime.now()) {
            return false;
        }
        if (program.limit_usage && program.total_order_count >= program.max_usage) {
            return false;
        }
        if (
            program.pricelist_ids.length > 0 &&
            (!this.pricelist_id ||
                !program.pricelist_ids.some((pl) => pl.id === this.pricelist_id.id))
        ) {
            return false;
        }
        return true;

    },

});


patch(PosStore.prototype, {
    async setup() {
        await super.setup(...arguments);
    
        this.bus.subscribe("loyalty.point", (payload) => {
            const { type: { name, session_id, loyalty_point } } = payload;
            const order = this.get_order();
    
            // Ensure order matches and session is valid, then continue.
            if (order.pos_reference !== name || order.session_id.id !== parseInt(session_id)) return;
    
            const rewards = this.getPotentialRewards();
            if (!rewards || !order.qr_reward_id) return;
    
            const selectedReward = rewards.find(({ reward }) => reward.id === order.qr_reward_id);
            if (!selectedReward) return;
    
            const { reward, coupon_id } = selectedReward;
            
            // Apply loyalty points to the reward.
            reward.discount_max_amount = loyalty_point;
            reward.required_points = loyalty_point;
    
            order._applyReward(reward, coupon_id);
    
            // Clear QR code after applying reward
            order.qr_code = '';
        });
    },
    

    getPotentialRewards() {
        const order = this.get_order();
        // Claimable rewards excluding those from eWallet programs.
        // eWallet rewards are handled in the eWalletButton.
        let rewards = [];
        if (order) {
            const claimableRewards = order.getClaimableRewards();
            rewards = claimableRewards.filter(
                ({ reward }) => reward.program_id.program_type !== "ewallet"
            );
        }
        const result = {};
        const discountRewards = rewards.filter(({ reward }) => reward.reward_type == "discount");
        const freeProductRewards = rewards.filter(({ reward }) => reward.reward_type == "product");
        const potentialFreeProductRewards = this.getPotentialFreeProductRewards();
        const avaiRewards = [
            ...potentialFreeProductRewards,
            ...discountRewards,
            ...freeProductRewards, // Free product rewards at the end of array to prioritize them
        ];

        for (const reward of avaiRewards) {
            result[reward.reward.id] = reward;
        }

        return Object.values(result);
    },


});
