# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import requests
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError

VOMSIS_ENDPOINT = 'https://developers.vomsis.com/api/v2'


class OnlineBankStatementProviderVomsis(models.Model):
    _inherit = 'online.bank.statement.provider'

    vomsis_app_key = fields.Char('Vomsis App Key')
    vomsis_app_secret = fields.Char('Vomsis App Secret')
    vomsis_jwt_token = fields.Text('JWT Token', readonly=True)
    vomsis_token_interval = fields.Datetime('Token Interval', default='2000-01-01 00:00:00')

    @api.model
    def _get_available_services(self):
        return super()._get_available_services() + [
            ('vomsis', 'Vomsis.com'),
        ]

    def _obtain_statement_data(self, date_since, date_until):
        self.ensure_one()
        if self.service != 'vomsis':
            return super()._obtain_statement_data(
                date_since,
                date_until,
            )
        return self._vomsis_obtain_statement_data(date_since, date_until)

    ##########
    # vomsis #
    ##########

    def _vomsis_get_request(self, endpoint, data=None):
        '''
        Sends GET request to Vomsis Endpoint
        :param endpoint:
        :param data:
        :return:
        '''
        headers = {'Content-Type': 'application/json',
                   'Authorization': "Bearer %s" % self.vomsis_jwt_token}
        response = requests.get(endpoint, params=data, headers=headers).json()

        if response.get('status') == 'success':
            return response
        else:
            raise UserError(_("Vomsis API Error."))

    def _vomsis_post_request(self, endpoint, data=None):
        '''
        Sends POST request to Vomsis Endpoint
        :param endpoint:
        :param data:
        :return:
        '''
        pass
        headers = {'Content-Type': 'application/json',
                   'Authorization': "Bearer %s" % self.vomsis_jwt_token}
        response = requests.post(endpoint, json=data, headers=headers)

        if response.get('status') == 'success':
            return response
        else:
            raise UserError(_("Vomsis API Error."))

    def _vomsis_get_auth(self):
        self.ensure_one()
        if self.vomsis_app_key and self.vomsis_app_secret:

            if not self.vomsis_jwt_token or self.vomsis_token_interval < datetime.now():
                vals = {'app_key': self.vomsis_app_key,
                        'app_secret': self.vomsis_app_secret}
                resp = requests.post("%s/authenticate" % VOMSIS_ENDPOINT, json=vals).json()
                if resp.get('status') == 'success':
                    self.write({'vomsis_jwt_token': resp.get('token'),
                                'vomsis_token_interval': datetime.now()})
        else:
            raise UserError(_('Please fill login and key.'))

    def _vomsis_get_transaction(self, account_id, date_since, date_until):
        page_url = "%s/accounts/%s/transactions" % (VOMSIS_ENDPOINT, account_id)

        vals = {'beginDate': date_since.strftime('%d-%m-%Y %H:%M:%S'),
                'endDate': date_until.strftime('%d-%m-%Y %H:%M:%S')}

        data = self._vomsis_get_request(endpoint=page_url, data=vals)
        if data.get('transactions'):
            return data.get('transactions')
        else:
            return []

    def _vomsis_date_from_string(self, date_str):
        """Vomsis dates are GMT+3, so we don't need to convert them to UTC
        """
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return dt

    def _vomsis_obtain_statement_data(self, date_since, date_until):
        self.ensure_one()
        self._vomsis_get_auth()
        journal = self.journal_id
        account_id = journal.vomsis_account_id

        if not account_id:
            raise UserError(
                _('Vomsis : wrong configuration, unknown account %s')
                % journal.bank_account_id.acc_number)
        transaction_lines = self._vomsis_get_transaction(
            account_id, date_since, date_until)
        new_transactions = []
        # transcation yoksa boş döndür
        # transcationun currency si, unique import idsi, amount'u
        # aynı gün içerisinde tekrar tekrar çekince noluo?
        sequence = 0
        for transaction in transaction_lines:
            sequence += 1
            date = self._vomsis_date_from_string(transaction.get('system_date'))
            vals_line = {
                'sequence': sequence,
                'date': date,
                'name': transaction.get('description', journal.name),
                'unique_import_id': str(transaction['id']),
                'amount': transaction['amount'],
            }
            new_transactions.append(vals_line)
        if new_transactions:
            return new_transactions, {}
        return
