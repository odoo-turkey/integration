/*
  Copyright 2022 Yiğit Budak (https://github.com/yibudak)
  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
*/

odoo.define('verimor_bulutsantralim_click2dial.systray.OpenCaller', function (require) {
"use strict";

var core = require('web.core');
var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');

var _t = core._t;

var FieldPhone = require('base_phone.updatedphone_widget').FieldPhone;

FieldPhone.include({
    showDialButton: function () {
        return true;
    }
});

});
