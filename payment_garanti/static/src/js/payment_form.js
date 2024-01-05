// Copyright 2024 Yiğit Budak (https://github.com/yibudak)
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
odoo.define('payment_garanti.payment_form', function (require) {
    "use strict";
    var PaymentForm = require('payment.payment_form');

    PaymentForm.include({
        /**
         Add select field to getFormData function
         * @override
         */
        getFormData: function (ev) {
            var $checkedRadio = this.$('input[type="radio"]:checked');
            if ($checkedRadio.length === 1 && $checkedRadio.data('provider') === 'garanti') {
                var acquirer_id = this.getAcquirerIdFromRadio($checkedRadio);
                var acquirer_form = false;
                if (this.isNewPaymentRadio($checkedRadio)) {
                    acquirer_form = this.$('#o_payment_add_token_acq_' + acquirer_id);
                } else {
                    acquirer_form = this.$('#o_payment_form_acq_' + acquirer_id);
                }
                // We've added select here
                var inputs_form = $('input,select', acquirer_form)
                return this._super.apply(this, [inputs_form]);
            } else {
                return this._super.apply(this, arguments);
            }
        },

    });
});