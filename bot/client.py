import hashlib
import hmac
import time
import logging
import requests
from urllib.parse import urlencode

logger = logging.getLogger('trading_bot.client')

TESTNET_BASE_URL = 'https://testnet.binancefuture.com'


class BinanceClient:
    def __init__(self, api_key, api_secret, base_url=TESTNET_BASE_URL):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/x-www-form-urlencoded',
        })
        logger.info('BinanceClient initialised. Base URL: %s', self.base_url)

    def _timestamp(self):
        return int(time.time() * 1000)

    def _sign(self, params):
        params['timestamp'] = self._timestamp()
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256,
        ).hexdigest()
        params['signature'] = signature
        return params

    def _request(self, method, endpoint, params=None, signed=False):
        params = params or {}
        if signed:
            params = self._sign(params)
        url = self.base_url + endpoint
        logger.debug('-> %s %s  params=%s', method, url,
                     {k: v for k, v in params.items() if k != 'signature'})
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=10)
            elif method.upper() == 'POST':
                response = self.session.post(url, data=params, timeout=10)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params, timeout=10)
            else:
                raise ValueError(f'Unsupported HTTP method: {method}')
            logger.debug('<- %s %s', response.status_code, response.text[:500])
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as exc:
            try:
                error_body = exc.response.json()
            except Exception:
                error_body = exc.response.text
            logger.error('HTTP error %s: %s', exc.response.status_code, error_body)
            raise
        except requests.exceptions.ConnectionError as exc:
            logger.error('Network connection error: %s', exc)
            raise
        except requests.exceptions.Timeout as exc:
            logger.error('Request timed out: %s', exc)
            raise

    def get_server_time(self):
        return self._request('GET', '/fapi/v1/time')

    def get_account_info(self):
        return self._request('GET', '/fapi/v2/account', signed=True)

    def get_exchange_info(self):
        return self._request('GET', '/fapi/v1/exchangeInfo')

    def place_order(self, params):
        logger.info('Placing order: %s', params)
        return self._request('POST', '/fapi/v1/order', params=params, signed=True)

    def get_open_orders(self, symbol=None):
        params = {}
        if symbol:
            params['symbol'] = symbol
        return self._request('GET', '/fapi/v1/openOrders', params=params, signed=True)

    def cancel_order(self, symbol, order_id):
        params = {'symbol': symbol, 'orderId': order_id}
        return self._request('DELETE', '/fapi/v1/order', params=params, signed=True)
