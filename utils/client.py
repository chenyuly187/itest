# -*- coding: utf-8 -*-

import requests
import socket
from suds.client import Client
from utils_exception import UnSupportMethod
from settings import *

METHODS = ['GET', 'POST', 'HEAD', 'TRACE', 'PUT', 'DELETE', 'OPTIONS', 'CONNECT']
logger = logging.getLogger('itest')


class HTTPClient(object):

    def __init__(self, url, method='GET', headers=None, cookies=None):
        """headers: Must be a dict. Such as headers={'Content_Type':'text/html'}"""
        self.url = url
        self.session = requests.session()
        self.method = method.upper()

        self._set_header(headers)
        self._set_cookie(cookies)

    def _set_header(self, headers):
        """set headers"""
        if headers:
            self.session.headers.update(headers)
            logger.debug('Set headers: {0}'.format(headers))

    def _set_cookie(self, cookies):
        """set cookies"""
        if cookies:
            self.session.cookies.update(cookies)
            logger.debug('Set cookies: {0}'.format(cookies))

    def _check_method(self):
        """检查传入的method是否可用。"""
        if self.method not in METHODS:
            logger.exception(UnSupportMethod(u'不支持的method:{0}，请检查传入参数！'.format(self.method)))
        else:
            return True

    def send(self, params=None, data=None, **kwargs):
        """send request to url.If response 200,return response, else return None."""
        if self._check_method():
            response = self.session.request(method=self.method, url=self.url, params=params, data=data, **kwargs)
            logger.debug('{0} {1}.'.format(self.method, self.url))
            if response:
                logger.debug(u'request success: {0}\n{1}'.format(response, response.content.strip().decode('utf-8')))
                return response
            else:
                logger.error('request failed: get None')


class TCPClient(object):

    def __init__(self, domain, port, timeout=30, max_receive=102400):
        self.domain = domain
        self.port = port
        self.connected = 0  # 连接后置为1
        self.max_receive = max_receive
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(timeout)

    def connect(self):
        """连接指定IP、端口"""
        if not self.connected:
            try:
                self._sock.connect((self.domain, self.port))
            except socket.error as e:
                logger.exception(e)
            else:
                self.connected = 1
                logger.debug('TCPClient connect to {0}:{1} success.'.format(self.domain, self.port))

    def send(self, send_string):
        """向服务器端发送send_string，并返回信息，若报错，则返回None"""
        self.connect()
        if self.connected:
            try:
                self._sock.send(send_string)
                logger.debug('TCPClient Send {0}'.format(send_string))
            except socket.error as e:
                logger.exception(e)

            try:
                rec = self._sock.recv(self.max_receive).decode('raw-unicode-escape').encode('utf-8')
                logger.debug(u'TCPClient received {0}'.format(rec.decode('utf-8')))
                return rec
            except socket.error as e:
                logger.exception(e)

    def close(self):
        """关闭连接"""
        if self.connected:
            self._sock.close()
            logger.debug('TCPClient closed.')

# TODO WebService  socketIO  WebSocket


class WebServiceClient(object):
    # todo complete client

    def __init__(self, url):

        self.client = Client(url)


# if __name__ == '__main__':
#     boce = TCPClient('192.168.6.63', 10011)
#     s = '[{"action": "query_spot_commodity_by_id", "data": {"commodity_id":"BRCM"}}]/**end**/'
#     r = boce.send(s)
#     print r
#     boce.close()


# if __name__ == '__main__':
#     sender = HTTPClient('http://www.baidu.com', 'get')
#     res = sender.send()
#     print res.status_code
#     print res.content

# if __name__ == '__main__':
#     c = WebServiceClient('http://ws.webxml.com.cn/WebServices/MobileCodeWS.asmx?WSDL')
#     print c.client
#     print c.client.service.getMobileCodeInfo('1560205', '')
