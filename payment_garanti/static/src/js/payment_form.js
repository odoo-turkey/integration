// Copyright 2022 Samet Altuntaş (https://github.com/samettal)
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
odoo.define('payment_garanti.payment_form', function (require) {
    "use strict";
    var rpc = require("web.rpc");
    var _t = core._t;
    var PaymentForm = require('payment.payment_form');
    ajax.loadXML('/payment_garanti/static/src/xml/payment_garanti_templates.xml', qweb);


    PaymentForm.include({
        /**
         * @override
         */
        payEvent: function (ev) {
            ev.preventDefault();
            var $checkedRadio = this.$('input[type="radio"]:checked');

            if ($checkedRadio.length === 1 && $checkedRadio.data('provider') === 'garanti' && this.isNewPaymentRadio($checkedRadio)) {
                return this._garanti_pay(ev, $checkedRadio);
            } else {
                return this._super.apply(this, arguments);
            }
        },


        _garanti_pay: function (ev, $checkedRadio, addPmEvent) {
            var self = this;
            if (ev.type === 'submit') {
                var button = $(ev.target).find('*[type="submit"]')[0]
            } else {
                var button = ev.target;
            }
            this.disableButton(button);
            var acquirerID = this.getAcquirerIdFromRadio($checkedRadio);
            var acquirerForm = this.$('#o_payment_add_token_acq_' + acquirerID);
            var inputsForm = $('input', acquirerForm);
            if (this.options.partnerId === undefined) {
                console.warn('payment_form: unset partner_id when adding new token; things could go wrong');
            }

            var formData = self.getFormData(inputsForm);
            var stripe = this.stripe;
            var card = this.stripe_card_element;
            if (card._invalid) {
                return;
            }
            return rpc.query({
                route: '/payment/stripe/s2s/create_setup_intent',
                params: {'acquirer_id': formData.acquirer_id}
            }).then(function (intent_secret) {
                // need to convert between ES6 promises and jQuery 2 deferred \o/
                return $.Deferred(function (defer) {
                    stripe.handleCardSetup(intent_secret, card)
                        .then(function (result) {
                            defer.resolve(result)
                        })
                });
            }).then(function (result) {
                if (result.error) {
                    return $.Deferred().reject({"message": {"data": {"message": result.error.message}}});
                } else {
                    _.extend(formData, {"payment_method": result.setupIntent.payment_method});
                    return rpc.query({
                        route: formData.data_set,
                        params: formData,
                    })
                }
            }).then(function (result) {
                if (addPmEvent) {
                    if (formData.return_url) {
                        window.location = formData.return_url;
                    } else {
                        window.location.reload();
                    }
                } else {
                    $checkedRadio.val(result.id);
                    self.el.submit();
                }
            }).fail(function (error, event) {
                // if the rpc fails, pretty obvious
                self.enableButton(button);
                self.displayError(
                    _t('Unable to save card'),
                    _t("We are not able to add your payment method at the moment. ") +
                    error.message.data.message
                );
            });
        }
    });
});