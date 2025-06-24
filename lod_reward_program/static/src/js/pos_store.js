import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Mutex } from "@web/core/utils/concurrency";
import { useService } from "@web/core/utils/hooks";

const mutex = new Mutex();
const updateRewardsMutex = new Mutex();

patch(PosStore.prototype, {

    updateRewards() {

        // Calls are not expected to take some time besides on the first load + when loyalty programs are made applicable
        if (this.models["loyalty.program"].length === 0) {
            return;
        }

        const order = this.get_order();
        if (order.finalized) {
            return;
        }
        updateRewardsMutex.exec(() => {
            return this.orderUpdateLoyaltyPrograms().then(async () => {
                try {
                    let changed = false;
                    if(this.config.is_auto_apply_reward){
                        let potentialFreeProductRewards = this.getPotentialFreeProductRewards()
                        let applyableRewards = [];

                        const selectedOrderline = this.get_order().get_selected_orderline()
                        for(let rewardObj of potentialFreeProductRewards){
                            if(rewardObj.reward.program_id.program_type == "buy_x_get_y" && rewardObj.reward.reward_product_ids.length > 0 && selectedOrderline !== undefined &&  selectedOrderline.qty > 0 && rewardObj.reward.program_id.trigger_product_ids.length > 0 && rewardObj.reward.program_id.trigger_product_ids[0].id == selectedOrderline.product_id.id){
                                applyableRewards.push(rewardObj);
                            }
                        }

                        if(applyableRewards.length > 0){
                            for(let rewardObj of applyableRewards){
                                await this._autoApplyReward(rewardObj.reward,rewardObj.coupon_id,rewardObj.potentialQty);
                            }
                            changed = true;
                        }
                        else{
                            // Get claimable rewards
                            const claimableRewards =  order.getClaimableRewards(false, false, true);


                            if(claimableRewards.length > 0){
                                // Remove all existing reward lines at the start
                                for (const line of order.lines) {
                                    if (line.is_reward_line && line.reward_id.program_id.program_type == "promotion") {
                                        order.removeOrderline(line);
                                        await line.delete();
                                    }

                                }

                                let product_with_reward = {};
                                // Collect all reward rule minimum quantities for claimable rewards
                                for (const line_1 of order.lines) {
                                    if (!line_1.is_reward_line) {
                                        let minimum_qty = [];
                                        for (const reward of claimableRewards){
                                            if(reward.reward.discount_product_ids){
                                                for (const product of reward.reward.discount_product_ids){

                                                    if (product.id == line_1.product_id.id){
                                                        if (reward.reward.rule_id && reward.reward.rule_id.minimum_qty){
                                                            minimum_qty.push(reward.reward.rule_id.minimum_qty);
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                        product_with_reward[line_1.product_id.id] = minimum_qty;

                                    }


                                }

                                for (const line of order.lines) {
                                    if (line.is_reward_line && line.reward_id.program_id.program_type == "promotion") {
                                         order.removeOrderline(line);
                                        await line.delete();
                                        //  order.uiState.disabledRewards.add(reward.id);
                                    }

                                }

                                for (const line of order.lines) {
                                    if (line.is_reward_line == true && line.reward_id.program_id.program_type == "promotion") {
                                         order.removeOrderline(line);
                                        await line.delete();
                                        //  order.uiState.disabledRewards.add(reward.id);
                                    }

                                }
                             

                                // Process each non-reward line
                                for (const line of order.lines) {
                                    if (!line.is_reward_line ) {
                                        if (product_with_reward[line.product_id.id] && product_with_reward[line.product_id.id].length >=1){
                                            // Find the closest minimum quantity match based on the line's quantity
                                            const closestRewardQty = product_with_reward[line.product_id.id].reduce((prev, curr) =>
                                                Math.abs(curr - line.qty) < Math.abs(prev - line.qty) ? curr : prev
                                            );

                                            // Apply the reward if the minimum quantity matches
                                            for (const { coupon_id, reward } of claimableRewards) {
                                                if (reward.rule_id && reward.rule_id.minimum_qty == closestRewardQty) {
                                                    for (const discount_pro of reward.discount_product_ids) {
                                                        if (discount_pro.id == line.product_id.id && line.qty!=0) {
                                                            await order._applyReward(reward, coupon_id);
                                                            changed = true;
                                                        }
                                                    }
                                                }
                                                else {
                                                    if (
                                                        reward.program_id.reward_ids.length === 1 &&
                                                        !reward.program_id.is_nominative &&
                                                        (reward.reward_type !== "product" ||
                                                            (reward.reward_type == "product" && !reward.multi_product))
                                                    ) {
                                                        await order._applyReward(reward, coupon_id);
                                                        changed = true;
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }

                        }
                    }
                    // If there were any changes, update the loyalty programs again
                    if (changed) {
                         await this.orderUpdateLoyaltyPrograms();
                    }
                    order._updateRewardLines();
                }catch (error) {
                    console.error('Error during reward application process:', error);
                }
            });
        });
    },
    async _autoApplyReward(reward, coupon_id, potentialQty) {
        const order = this.get_order();
        order.uiState.disabledRewards.delete(reward.id);
        const productsList = reward.reward_product_ids;
        if(!productsList) {
            return false;
        }
        if((reward.program_id.applies_on !== "both") ||(reward.program_id.applies_on == "both" && potentialQty)) {
            for(var product of productsList){
                await this._autoAddLineToCurrentOrder(
                    {
                        product_id: product ,
                        qty: potentialQty || 1,
                    },
                    {}
                );
                const result = order._applyReward(reward, coupon_id, {'product': product });
                if (result !== true) {
                    // Returned an error
                    this.notification.add(result);
                }
            }

            return true;
        }
        else {
            for(var product of productsList){
                const result = order._applyReward(reward, coupon_id, {'product' : product});
                if (result !== true) {
                    // Returned an error
                    this.notification.add(result);
                }
            }
            return true;
        }
    },
    async _autoAddLineToCurrentOrder(vals, opt = {}, configure = true) {
        const product = vals.product_id;
        const order = this.get_order();
        const linkedPrograms = (
            this.models["loyalty.program"].getBy("trigger_product_ids", product.id) || []
        ).filter((p) => ["gift_card", "ewallet"].includes(p.program_type));
        let selectedProgram = null;
        if (linkedPrograms.length > 1) {
            selectedProgram = await makeAwaitable(this.dialog, SelectionPopup, {
                title: _t("Select program"),
                list: linkedPrograms.map((program) => ({
                    id: program.id,
                    item: program,
                    label: program.name,
                })),
            });
            if (!selectedProgram) {
                return;
            }
        } else if (linkedPrograms.length === 1) {
            selectedProgram = linkedPrograms[0];
        }

        const orderTotal = this.get_order().get_total_with_tax();
        if (
            selectedProgram &&
            ["gift_card", "ewallet"].includes(selectedProgram.program_type) &&
            orderTotal < 0
        ) {
            opt.price_unit = -orderTotal;
        }
        if (selectedProgram && selectedProgram.program_type == "gift_card") {
            const shouldProceed = await this._setupGiftCardOptions(selectedProgram, opt);
            if (!shouldProceed) {
                return;
            }
        } else if (selectedProgram && selectedProgram.program_type == "ewallet") {
            const shouldProceed = await this.setupEWalletOptions(selectedProgram, opt);
            if (!shouldProceed) {
                return;
            }
        }

        // move price_unit from opt to vals
        if (opt.price_unit !== undefined) {
            vals.price_unit = opt.price_unit;
            delete opt.price_unit;
        }

        if (!order) {
            order = this.add_new_order();
        }
        this.addPendingOrder([order.id]);
        const result = await this.addLineToOrder(vals, order, opt, configure);

        await this.updatePrograms();

        return result;
    },
})