# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Bo Maryniuk <bo@suse.de>`
'''

from __future__ import absolute_import, print_function, unicode_literals
from tests.support.unit import TestCase, skipIf
from tests.support.mock import (
    NO_MOCK,
    NO_MOCK_REASON,
    MagicMock,
    patch)

# Import Salt libs
import salt.exceptions
import salt.state
from salt.utils import ssdp

try:
    import pytest
except ImportError as err:
    pytest = None


class Mocks(object):
    def get_socket_mock(self, expected_ip, expected_hostname):
        '''
        Get a mock of a socket
        :return:
        '''
        sck = MagicMock()
        sck.getsockname = MagicMock(return_value=(expected_ip, 123456))

        sock_mock = MagicMock()
        sock_mock.socket = MagicMock(return_value=sck)
        sock_mock.gethostbyname = MagicMock(return_value=expected_hostname)

        return sock_mock


@skipIf(NO_MOCK, NO_MOCK_REASON)
@skipIf(pytest is None, 'PyTest is missing')
class SSDPBaseTestCase(TestCase, Mocks):
    '''
    TestCase for SSDP-related parts.
    '''

    @patch('salt.utils.ssdp._json', None)
    @patch('salt.utils.ssdp.asyncio', None)
    def test_base_avail(self):
        '''
        Test SSDP base class availability method.
        :return:
        '''
        base = ssdp.SSDPBase()
        assert not base._is_available()

        with patch('salt.utils.ssdp._json', True):
            assert not base._is_available()

        with patch('salt.utils.ssdp.asyncio', True):
            assert not base._is_available()

        with patch('salt.utils.ssdp._json', True), patch('salt.utils.ssdp.asyncio', True):
            assert base._is_available()

    def test_base_protocol_settings(self):
        '''
        Tests default constants data.
        :return:
        '''
        base = ssdp.SSDPBase()
        v_keys = ['signature', 'answer', 'port', 'listen_ip', 'timeout']
        v_vals = ['__salt_master_service', {}, 4520, '0.0.0.0', 3]
        for key in v_keys:
            assert key in base.DEFAULTS

        for key in base.DEFAULTS.keys():
            assert key in v_keys

        for key, value in zip(v_keys, v_vals):
            assert base.DEFAULTS[key] == value

    def test_base_self_ip(self):
        '''
        Test getting self IP method.

        :return:
        '''
        def boom():
            '''
            Side effect
            :return:
            '''
            raise Exception('some network error')

        base = ssdp.SSDPBase()
        expected_ip = '192.168.1.10'
        expected_host = 'oxygen'
        sock_mock = self.get_socket_mock(expected_ip, expected_host)

        with patch('salt.utils.ssdp.socket', sock_mock):
            assert base.get_self_ip() == expected_ip

        sock_mock.socket().getsockname.side_effect = boom
        with patch('salt.utils.ssdp.socket', sock_mock):
            assert base.get_self_ip() == expected_host


@skipIf(NO_MOCK, NO_MOCK_REASON)
@skipIf(pytest is None, 'PyTest is missing')
class SSDPFactoryTestCase(TestCase):
    '''
    Test socket protocol
    '''
    @patch('salt.utils.ssdp.socket.gethostbyname', MagicMock(return_value='10.10.10.10'))
    def test_attr_check(self):
        '''
        Tests attributes are set to the base class

        :return:
        '''
        config = {
            ssdp.SSDPBase.SIGNATURE: '-signature-',
            ssdp.SSDPBase.ANSWER: {'this-is': 'the-answer'}
        }
        factory = ssdp.SSDPFactory(**config)
        for attr in [ssdp.SSDPBase.SIGNATURE, ssdp.SSDPBase.ANSWER]:
            assert hasattr(factory, attr)
            assert getattr(factory, attr) == config[attr]
        assert not factory.disable_hidden
        assert factory.my_ip == '10.10.10.10'
