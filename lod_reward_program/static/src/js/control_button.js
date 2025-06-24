import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    getClaimableRewards(coupon_id = false, program_id = false, auto = false) {
        const couponPointChanges = this.uiState.couponPointChanges;
        const excludedCouponIds = Object.keys(couponPointChanges)
            .filter((id) => couponPointChanges[id].manual && couponPointChanges[id].existing_code)
            .map((id) => couponPointChanges[id].coupon_id);

        const allCouponPrograms = Object.values(this.uiState.couponPointChanges)
            .filter((pe) => !excludedCouponIds.includes(pe.coupon_id))
            .map((pe) => ({
                program_id: pe.program_id,
                coupon_id: pe.coupon_id,
            }))
            .concat(
                this._code_activated_coupon_ids.map((coupon) => ({
                    program_id: coupon.program_id.id,
                    coupon_id: coupon.id,
                }))
            );
        const result = [];
        const totalWithTax = this.get_total_with_tax();
        const totalWithoutTax = this.get_total_without_tax();
        const totalIsZero = totalWithTax === 0;
        const globalDiscountLines = this._getGlobalDiscountLines();
        const globalDiscountPercent = globalDiscountLines.length
            ? globalDiscountLines[0].reward_id.discount
            : 0;
        for (const couponProgram of allCouponPrograms) {
            const program = this.models["loyalty.program"].get(couponProgram.program_id);
            if (
                program.pricelist_ids.length > 0 &&
                (!this.pricelist_id ||
                    !program.pricelist_ids.some((pl) => pl.id === this.pricelist_id.id))
            ) {
                continue;
            }
            if (program.trigger == "with_code") {
                // For coupon programs, the rules become conditions.
                // Points to purchase rewards will only come from the scanned coupon.
                if (!this._canGenerateRewards(program, totalWithTax, totalWithoutTax)) {
                    continue;
                }
            }
            if (
                (coupon_id && couponProgram.coupon_id !== coupon_id) ||
                (program_id && couponProgram.program_id !== program_id)
            ) {
                continue;
            }
            const points = this._getRealCouponPoints(couponProgram.coupon_id);
            for (const reward of program.reward_ids) {
                // if (points < reward.required_points) {
                //     continue;
                // }
                if (auto && this.uiState.disabledRewards.has(reward.id)) {
                    continue;
                }
                // Try to filter out rewards that will not be claimable anyway.
                if (reward.is_global_discount && reward.discount <= globalDiscountPercent) {
                    continue;
                }
                if (reward.reward_type === "discount" && totalIsZero) {
                    continue;
                }
                let unclaimedQty;
                if (reward.reward_type === "product") {
                    if (!reward.multi_product) {
                        const product = reward.reward_product_id;
                        if (!product) {
                            continue;
                        }
                        unclaimedQty = this._computeUnclaimedFreeProductQty(
                            reward,
                            couponProgram.coupon_id,
                            product,
                            points
                        );
                    }
                    if (!unclaimedQty || unclaimedQty <= 0) {
                        continue;
                    }
                }
                result.push({
                    coupon_id: couponProgram.coupon_id,
                    reward: reward,
                    potentialQty: unclaimedQty,
                });
            }
        }
        return result;
    },
   
});
