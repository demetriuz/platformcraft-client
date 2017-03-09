# -*- coding: utf-8 -*-
import hashlib
import hmac
from io import BytesIO

from mock import Mock, patch
from nose.tools import assert_equal

from platformcraft.client import PlatformcraftClient


TIMESTAMP = 1450342665


@patch('platformcraft.client.time.time', Mock(return_value=TIMESTAMP))
class TestClient(object):
    def test_get_url(self):
        url = self.client._get_url(endpoint_path='endpoint1', method='GET', arg1='aaa', arg2='bbb')

        hash = hmac.new(
            self.key,
            'GET+' + self.client.api_url + 'endpoint1?apiuserid={apiuserid}&timestamp={timestamp}'.format(apiuserid=self.apiuserid, timestamp=TIMESTAMP),
            digestmod=hashlib.sha256
        ).hexdigest()

        expected_url = 'https://{api_url}endpoint1?arg1=aaa&arg2=bbb&apiuserid={apiuserid}&hash={hash}&timestamp={timestamp}'\
            .format(api_url=self.client.api_url, apiuserid=self.apiuserid, timestamp=TIMESTAMP, hash=hash)

        assert_equal(expected_url, url)

    def test_get_object(self):
        self.client._get_url = Mock(return_value='http://api.test/objects/objectid')

        res = self.client.get_object('objectid')

        self.client._get_url.assert_called_once_with(endpoint_path='objects/objectid')
        self.client._api_get.assert_called_once_with('http://api.test/objects/objectid')
        assert res

    def test_get_objects(self):
        self.client._get_url = Mock(return_value='http://api.test/objects/')

        res = self.client.get_objects()

        self.client._get_url.assert_called_once_with(endpoint_path='objects', ext=None, folder=None, name=None)
        self.client._api_get.assert_called_once_with('http://api.test/objects/')
        assert res

    def test_create_object(self):
        f = BytesIO()
        self.client._get_url = Mock(return_value='http://api.test/objects/')
        res = self.client.create_object(file_=f, name='filename.jpg')
        self.client._get_url.assert_called_once_with(endpoint_path='objects', method='POST', name='filename.jpg')
        self.client._api_post.assert_called_once_with('http://api.test/objects/', data={'name': 'filename.jpg'},
                                                      files={'file': f})
        assert res

    def test_download(self):
        self.client._get_url = Mock(return_value='http://api.test/download/')

        res = self.client.download(
            'http://example.com/path/to/img.jpg',
            path='/aaa/',
            name='img.jpg'
        )

        self.client._get_url.assert_called_once_with(endpoint_path='download', method='POST', path='/aaa/',
                                                     name='img.jpg', url='http://example.com/path/to/img.jpg')
        self.client._api_post.assert_called_once_with('http://api.test/download/',
                                                      data={
                                                          'url': 'http://example.com/path/to/img.jpg',
                                                          'path': '/aaa/',
                                                          'name': 'img.jpg'
                                                      })
        assert res

    def setUp(self):
        self.key = 'testkey'
        self.apiuserid = 'testid'

        self.client = PlatformcraftClient(apiuserid=self.apiuserid, key=self.key)
        self.client._api_get = Mock()
        self.client._api_post = Mock()
