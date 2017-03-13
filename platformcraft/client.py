# -*- coding: utf-8 -*-
import hashlib
import hmac
import urlparse
import requests
import time
from urllib import urlencode


class PlatformcraftClient(object):
    api_url = 'api.platformcraft.ru/1/'

    def __init__(self, apiuserid, key):
        self.apiuserid = apiuserid
        self.key = key

    def get_objects(self, folder=None, name=None, ext=None):
        url = self._get_url(endpoint_path='objects', folder=folder, name=name, ext=ext)
        return self._api_get(url)

    def get_object(self, id_):
        url = self._get_url(endpoint_path='objects/{}'.format(id_))
        return self._api_get(url)

    def create_object(self, file_, name=None):
        data = dict(name=name)
        url = self._get_url(endpoint_path='objects', method='POST', **data)
        return self._api_post(url, data=dict(**data), files={'file': file_})

    def download(self, url, path=None, name=None):
        data = dict(url=url, path=path, name=name)
        url = self._get_url(endpoint_path='download', method='POST', **data)
        return self._api_post(url, data=data)

    def _get_hmac_params(self):
        return [('apiuserid', self.apiuserid), ('timestamp', int(time.time()))]

    def _normalize_params(self, **params):
        actual_params = [
            (k, v) for k, v in
            params.items()
            if v is not None
        ]
        return sorted(actual_params)

    def _get_url(self, endpoint_path, method='GET', **kwargs):
        actual_params = self._normalize_params(**kwargs)
        actual_params.extend(self._get_hmac_params())

        full_endpoint_path = urlparse.urljoin(self.api_url, endpoint_path)

        hmac_str = hmac.new(
            self.key,
            method + '+' + full_endpoint_path + '?' + urlencode(self._get_hmac_params()),
            digestmod=hashlib.sha256
        ).hexdigest()

        signed_encoded_query = urlencode(dict(actual_params, hash=hmac_str))
        signed_full_endpoint_path_with_query = 'https://' + full_endpoint_path + '?' + signed_encoded_query

        return signed_full_endpoint_path_with_query

    def _api_get(self, *args, **kwargs):
        return requests.get(*args, **kwargs).json()

    def _api_post(self, *args, **kwargs):
        return requests.post(*args, **kwargs).json()
