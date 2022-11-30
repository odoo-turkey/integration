// Copyright 2022 Yiğit Budak (https://github.com/yibudak)
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

odoo.define('payment_moka.payment_form', require => {
    'use strict';

    const core = require('web.core');
    const checkoutForm = require('payment.checkout_form');
    const manageForm = require('payment.manage_form');
    const _t = core._t;

    this.$("[name='cardNumber']").on("keydown", function (e) {
        var cursor = this.selectionStart;
        if (this.selectionEnd != cursor) return;
        if (e.which == 46) {
            if (this.value[cursor] == " ") this.selectionStart++;
        } else if (e.which == 8) {
            if (cursor && this.value[cursor - 1] == " ") this.selectionEnd--;
        }
    }).on("input", function () {
        var value = this.value;
        var cursor = this.selectionStart;
        var matches = value.substring(0, cursor).match(/[^0-9]/g);
        if (matches) cursor -= matches.length;
        value = value.replace(/[^0-9]/g, "").substring(0, 16);
        var formatted = "";
        for (var i = 0, n = value.length; i < n; i++) {
            if (i && i % 4 == 0) {
                if (formatted.length <= cursor) cursor++;
                formatted += " ";
            }
            formatted += value[i];
        }
        if (formatted == this.value) return;
        this.value = formatted;
        this.selectionEnd = cursor;
    });

    const paymentMokaMixin = {

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * Simulate a feedback from a payment provider and redirect the customer to the status page.
         *
         * @override method from payment.payment_form_mixin
         * @private
         * @param {string} code - The code of the provider
         * @param {number} providerId - The id of the provider handling the transaction
         * @param {object} processingValues - The processing values of the transaction
         * @return {Promise}
         */
        _processDirectPayment: function (code, providerId, processingValues) {
            if (code !== 'moka') {
                return this._super(...arguments);
            }

            return this._rpc({
                route: '/payment/moka/payments',
                params: {
                    'provider_id': providerId,
                    'reference': processingValues.reference,
                    'amount': processingValues.amount,
                    'currency_id': processingValues.currency_id,
                    'partner_id': processingValues.partner_id,
                    'access_token': processingValues.access_token,
                    'card_args': {
                        'card_name': $("[name='cardName']").val(),
                        'card_number': $("[name='cardNumber']").val(),
                        'card_valid_month': $("[name='validMonth']").val(),
                        'card_valid_year': $("[name='validYear']").val(),
                        'card_cvv': $("[name='cardCVV']").val(),
                    }
                },
            }).then(paymentResponse => {
                if (paymentResponse.redirect_url) {
                    window.location = paymentResponse.redirect_url;
                }
            }).guardedCatch((error) => {
                error.event.preventDefault();
                this._displayError(
                    _t("Server Error"),
                    _t("We are not able to process your payment."),
                    error.message.data.message
                );
            });
        },

        /**
         * Prepare the inline form of Moka for direct payment.
         *
         * @override method from payment.payment_form_mixin
         * @private
         * @param {string} code - The code of the selected payment option's provider
         * @param {integer} paymentOptionId - The id of the selected payment option
         * @param {string} flow - The online payment flow of the selected payment option
         * @return {Promise}
         */
        _prepareInlineForm: function (code, paymentOptionId, flow) {
            if (code !== 'moka') {
                return this._super(...arguments);
            } else if (flow === 'token') {
                return Promise.resolve();
            }
            this._setPaymentFlow('direct');
            return Promise.resolve()
        },
    };
    checkoutForm.include(paymentMokaMixin);
    manageForm.include(paymentMokaMixin);
});