from telegram.ext import Updater
from telegram.utils.webhookhandler import (WebhookServer, WebhookHandler)
from urllib.parse import urlparse, parse_qs
import logging


class MyUpdater(Updater):
    def __init__(self,
                 token=None,
                 base_url=None,
                 workers=4,
                 bot=None,
                 user_sig_handler=None,
                 request_kwargs=None):
        super().__init__(token, base_url, workers, bot, user_sig_handler, request_kwargs)

    def _start_webhook(self, listen, port, url_path, cert, key, bootstrap_retries, clean,
                       webhook_url, allowed_updates):

        self.logger.debug('Updater thread started')
        use_ssl = cert is not None and key is not None
        if not url_path.startswith('/'):
            url_path = '/{0}'.format(url_path)

        # Create and start server
        self.httpd = MyWebhookServer((listen, port), self.update_queue, url_path, self.bot)
        if use_ssl:
            self._check_ssl_cert(cert, key)

            # DO NOT CHANGE: Only set webhook if SSL is handled by library
            if not webhook_url:
                webhook_url = self._gen_webhook_url(listen, port, url_path)

            self._bootstrap(
                max_retries=bootstrap_retries,
                clean=clean,
                webhook_url=webhook_url,
                cert=open(cert, 'rb'),
                allowed_updates=allowed_updates)
        elif clean:
            self.logger.warning("cleaning updates is not supported if "
                                "SSL-termination happens elsewhere; skipping")

        self.httpd.serve_forever(poll_interval=1)


class MyWebhookServer(WebhookServer, object):
    query_params = {}

    def __init__(self, server_address, update_queue, webhook_path, bot):
        super().__init__(server_address, M_WebhookHandler, update_queue, webhook_path, bot)


class M_WebhookHandler(WebhookHandler, object):
    server_version = 'WebhookHandler/1.0'

    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger(__name__)
        super(WebhookHandler, self).__init__(request, client_address, server)

    def do_GET(self):
        print('Very get_ request so much fun hahahahahahhahaha : HEADERS')
        print(self.headers)
        print('PATH: %s' % self.path)
        #if 'code' in self.path:
        self.server.query_params['code'] = parse_qs(urlparse(self.path).query)['code'][0]
        self.send_response(200)
        self.end_headers()