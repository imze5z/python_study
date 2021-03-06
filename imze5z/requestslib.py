# -*- encoding: utf-8 -*-

import requests
from collections import OrderDict
from requests.utils import dict_from_cookiejar


class HTTP(object):
    def __init__(self, session=False):
        if session:
            self.session = requests.Session()

    def close(self):
        if self.session:
            self.session.close()

    def get_session_cookie():
        if session:
            return dict_from_cookiejar(self.session.cookies)

    def get(self,
            url,
            headers=None,
            cookies=None,
            timeout=30,
            verify=False,
            proxies=None):
        if self.session:
            r = self.session.get(url,
                                 headers=OrderDict(headers),
                                 cookies=cookies,
                                 timeout=timeout,
                                 verify=verify,
                                 proxies=proxies)
            r.raise_for_status()
            r.encoding = 'utf-8'
            return r.text, r.headers, dict_from_cookiejar(r.cookies), r.history
        else:
            r = requests.get(url,
                             headers=OrderDict(headers),
                             cookies=cookies,
                             timeout=timeout,
                             verify=verify,
                             proxies=proxies)
            r.raise_for_status()
            r.encoding = 'utf-8'
            return r.text, r.headers, dict_from_cookiejar(r.cookies), r.history

    def post(self,
             url,
             headers=None,
             cookies=None,
             timeout=30,
             data={},
             verify=False,
             proxies=None):
        if self.session:
            r = self.session.post(
                url,
                headers=OrderDict(headers),
                cookies=cookies,
                timeout=timeout,
                data=data,
                verify=verify,
                proxies=proxies)
            r.raise_for_status()
            r.encoding = 'utf-8'
            return r.text, r.headers, dict_from_cookiejar(r.cookies), r.history
        else:
            r = requests.post(
                url,
                headers=OrderDict(headers),
                cookies=cookies,
                timeout=timeout,
                data=data,
                verify=verify,
                proxies=proxies)
            r.raise_for_status()
            r.encoding = 'utf-8'
            return r.text, r.headers, dict_from_cookiejar(r.cookies), r.history
