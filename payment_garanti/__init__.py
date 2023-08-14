# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import controllers
from . import models

# from odoo.addons.payment import setup_provider, reset_payment_provider
from odoo.addons.payment import reset_payment_provider
from odoo.addons.payment.models.payment_acquirer import create_missing_journal_for_acquirers

#
#
# def post_init_hook(cr, registry):
#     setup_provider(cr, registry, 'garanti')


def uninstall_hook(cr, registry):
    reset_payment_provider(cr, registry, 'garanti')
