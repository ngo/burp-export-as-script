from pprint import pformat
from collections import defaultdict
import urlparse
from Cookie import BaseCookie

PROLOGUE = """#!/usr/bin/env python
import requests
import re
import logging

logging.basicConfig(format="%(asctime)-15s\t%(levelname)s\t%(name)s\t%(message)s")
logging.getLogger().setLevel(logging.{loglevel})

logger = logging.getLogger("main")

session = requests.Session()
"""

SSL_DISABLE = """
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
"""

PROXY_ENABLE = """
session.proxies = {{
    'http' : {proxy},
    'https' : {proxy}
}}
"""


REQUEST_TEMPLATE = """
headers_{idx} = {headers}
data_{idx} = {data}

response_{idx} = session.{method}(
    url={url},
    headers=headers_{idx},
    data=data_{idx},
    verify={verify}
)

#logger.info(response_{idx}.text)
"""

def generate_request(http_message, index, verify, no_cookies):
    req_info = http_message.req_info
    req_data = http_message.req_data
    headers = (header.split(': ', 1) for header in req_info.getHeaders()[1:])
    if no_cookies:
        headers = dict(filter(lambda x: x[0].lower() != 'cookie', headers))
    else:
        headers = dict(headers)
    method = req_info.getMethod().lower()
    url = pformat(str(req_info.getUrl()))
    data = pformat(bytearray(req_data[req_info.getBodyOffset():]))
    return REQUEST_TEMPLATE.format(
        headers=pformat(headers),
        data=data,
        url=url,
        method=method,
        idx=index,
        verify=verify
    )

def get_all_unique_cookies(messages):
    all_cookies = defaultdict(dict)
    for message in messages:
        domain = urlparse.urlparse(str(message.req_info.getUrl())).netloc
        domain = domain.split(':')[0]
        message_cookies = filter(
                    lambda x: x[0].lower() == 'cookie',
                    (
                        header.split(': ', 1) 
                        for header in message.req_info.getHeaders()[1:]
                    )
        )
        for cookie_header in message_cookies:
            cook = BaseCookie(str(cookie_header[1]))
            for name in cook:
                all_cookies[domain][name] = cook[name].value
    for domain, cooks in all_cookies.items():
        for name, value in cooks.items():
            yield domain, name, value

def generate_script(messages, disable_ssl_verification=False, proxy=None, loglevel="DEBUG", auto_cookie=False):
    snippets = [PROLOGUE.format(loglevel=loglevel)]
    if disable_ssl_verification:
        snippets.append(SSL_DISABLE)
    if proxy:
        snippets.append(PROXY_ENABLE.format(proxy=repr(proxy)))
    if auto_cookie:
        for domain, name, value in get_all_unique_cookies(messages):
            snippets.append(
                    "session.cookies.set({name}, {value}, domain={domain})\n".format(
                        name=repr(name), value=repr(value), domain=repr(domain)
                    )
            )
    for idx, message in enumerate(messages):
        snippets.append(generate_request(message, idx, not disable_ssl_verification, auto_cookie))
    return "".join(snippets)
