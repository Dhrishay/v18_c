/* @odoo-module */
import { WebsiteSale } from "@website_sale/js/website_sale";
import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";
import wUtils from "@website/js/utils";
import {
    ProductConfiguratorDialog
} from '@sale/js/product_configurator_dialog/product_configurator_dialog';
import { serializeDateTime } from '@web/core/l10n/dates';
import { cartHandlerMixin } from '@website_sale/js/website_sale_utils';

const { DateTime } = luxon;

WebsiteSale.include({
    _openProductConfigurator(isOnProductPage) {
        this.call('dialog', 'add', ProductConfiguratorDialog, {
            productTemplateId: this.rootProduct.product_template_id,
            ptavIds: this.rootProduct.variant_values,
            customPtavs: this.rootProduct.product_custom_attribute_values.map(
                customPtav => ({
                    id: customPtav.custom_product_template_attribute_value_id,
                    value: customPtav.custom_value,
                })
            ),
            quantity: this.rootProduct.quantity,
            soDate: serializeDateTime(DateTime.now()),
            edit: false,
            isFrontend: true,
            options: {
                isMainProductConfigurable: !isOnProductPage,
                showQuantity: Boolean(document.querySelector('.js_add_cart_json')),
            },
            save: async (mainProduct, optionalProducts, options) => {
                this._trackProducts([mainProduct, ...optionalProducts]);

                const values = await rpc('/website_sale/product_configurator/update_cart', {
                    main_product: this._serializeProduct(mainProduct),
                    optional_products: optionalProducts.map(this._serializeProduct),
                    ...this._getAdditionalRpcParams(),
                });
                if (!values) {
                    const warningMessage = document.createElement('div');
                    warningMessage.className = 'alert alert-warning mt-2';
                    warningMessage.textContent = 'Adding to cart is currently not allowed. You can place orders between 10:00 AM and 12:00 PM.';

                    // Insert after the add to cart button
                    const addToCartWrap = document.querySelector('#add_to_cart_wrap');

                    // Remove any existing warning
                    const existingWarning = addToCartWrap.nextElementSibling;
                    if (existingWarning && existingWarning.classList.contains('alert-warning')) {
                        existingWarning.remove();
                    }

                    // Append new warning
                    addToCartWrap.parentNode.insertBefore(warningMessage, addToCartWrap.nextSibling);

                    return; // Exit early if there's a warning
                }
                this._onConfigured(options, values);
            },
            discard: () => {},
            ...this._getAdditionalDialogProps(),
        });
    },

});

function showCartNotification(callService, props, options = {}) {
    // Show the notification about the cart
    if (props.lines) {
        callService("cartNotificationService", "add", _t("Item(s) added to your cart"), {
            lines: props.lines,
            currency_id: props.currency_id,
            ...options,
        });
    }
    if (props.warning) {
        callService("cartNotificationService", "add", _t("Warning"), {
            warning: props.warning,
            ...options,
        });
    }
}

function updateCartNavBar(data) {
    sessionStorage.setItem('website_sale_cart_quantity', data.cart_quantity);
    $(".my_cart_quantity")
        .parents('li.o_wsale_my_cart').removeClass('d-none').end()
        .toggleClass('d-none', data.cart_quantity === 0)
        .addClass('o_mycart_zoom_animation').delay(300)
        .queue(function () {
            $(this)
                .toggleClass('fa fa-warning', !data.cart_quantity)
                .attr('title', data.warning)
                .text(data.cart_quantity || '')
                .removeClass('o_mycart_zoom_animation')
                .dequeue();
        });

    $(".js_cart_lines").first().before(data['website_sale.cart_lines']).end().remove();
    $("#cart_total").replaceWith(data['website_sale.total']);
    if (data.cart_ready) {
        document.querySelector("a[name='website_sale_main_button']")?.classList.remove('disabled');
    } else {
        document.querySelector("a[name='website_sale_main_button']")?.classList.add('disabled');
    }
}

publicWidget.registry.WebsiteSale = publicWidget.registry.WebsiteSale.extend({
    init : function () {
        this._super.apply(this, arguments);
    },
    addToCart(params) {
        if (this.isBuyNow) {
            params.express = true;
        } else if (this.stayOnPageOption) {
            return this._addToCartInPage(params);
        }
        return wUtils.sendRequest('/shop/cart/update', params);
    },

    async _addToCartInPage(params) {
        const data = await rpc("/shop/cart/update_json", {
            ...params,
            display: false,
            force_create: true,
        });
        if (data.warning) {
            const warningMessage = document.createElement('div');
            warningMessage.className = 'alert alert-warning mt-2';
            warningMessage.textContent = data.warning;
            const addToCartWrap = document.querySelector('#add_to_cart_wrap');
            const existingWarning = addToCartWrap.nextElementSibling;
            if (existingWarning && existingWarning.classList.contains('alert-warning')) {
                existingWarning.remove();
            }
            addToCartWrap.parentNode.insertBefore(warningMessage, addToCartWrap.nextSibling);

            return;
        }
        if (data.cart_quantity && (data.cart_quantity !== parseInt($(".my_cart_quantity").text()))) {
            updateCartNavBar(data);
        };
        showCartNotification(this.call.bind(this), data.notification_info);
        return data;
    },
    submitForm: function () {
        const params = this.rootProdu
        const $product = $('#product_detail');
        const productTrackingInfo = $product.data('product-tracking-info');
        if (productTrackingInfo) {
            productTrackingInfo.quantity = params.quantity;
            $product.trigger('add_to_cart_event', [productTrackingInfo]);
        }

        params.add_qty = params.quantity;
        params.product_custom_attribute_values = JSON.stringify(params.product_custom_attribute_values);
        params.no_variant_attribute_values = JSON.stringify(params.no_variant_attribute_values);
        delete params.quantity;
        return this.TimeRestrict(params);
    },
});

