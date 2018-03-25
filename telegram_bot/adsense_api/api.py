# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import


import argparse
import os
import logging
from googleapiclient import discovery
from googleapiclient.http import build_http
from oauth2client import client, tools
from oauth2client import file

from telegram_bot import bot_main, config
from telegram_bot.entities.domain_entities import ReportParams, CException

logger = logging.getLogger(__name__)


class AdSenseAPIClientv2(object):
    _scope = 'https://www.googleapis.com/auth/adsense.readonly'
    argparser = argparse.ArgumentParser(add_help=False)
    argparser.add_argument('--report_id', help='The ID of the saved report to generate')
    _client_secrets = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

    def __init__(self, callback, user_id=None, *args):
        self.callback = callback
        self.user_id = user_id
        self.args = args
        self.flags = self.build_arg_parsers().parse_args([])
        self.service = self.build_service('adsense', 'v1.4')

    def build_service(self, name, version):
        flow = client.flow_from_clientsecrets(self._client_secrets,
                                              scope=self._scope,
                                              message=tools.message_if_missing(self._client_secrets))
        storage = file.Storage(str(self.user_id) + '.dat')
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            print('authorization_flow')
            credentials = self.authorization_flow(flow, storage)
        http = credentials.authorize(http=build_http())
        return discovery.build(name, version, http=http)

    def build_arg_parsers(self):
        parent_parsers = [tools.argparser]
        parent_parsers.extend([self.argparser])
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=parent_parsers)
        return parser

    def authorization_flow(self, flow, storage, http=None):
        flow.redirect_uri = config.global_config.web_host
        authorize_url = flow.step1_get_authorize_url()
        if not self.args:
            self.callback(authorize_url)
        else:
            self.callback(self.args[0], authorize_url)
        code = None
        bot_main.webserver.handle_request()
        if 'error' in bot_main.webserver.query_params:
            raise CException('Authentication request was rejected.')
        if 'code' in bot_main.webserver.query_params:
            code = bot_main.webserver.query_params['code']
        else:
            raise CException('Authentication request was rejected.')
        try:
            credential = flow.step2_exchange(code, http=http)
        except client.FlowExchangeError as e:
            logger.error('%s happend to %s' % (e, str(self.user_id)))
            raise CException('Authentication has failed')
        storage.put(credential)
        credential.set_store(storage)
        logger.debug('Authentication successful.')
        return credential

    def get_report_by_params(self, params):
        return self.service.accounts().reports().generate(
                    accountId=params.account_id,
                    startDate=params.start_date,
                    endDate=params.end_date,
                    metric=params.metrics,
                    dimension=params.dimension,
                    sort=params.sort).execute()

    def get_default_report(self, account_id):
        return self.get_report_by_params(ReportParams(**{'account_id': account_id}))