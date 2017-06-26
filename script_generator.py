from pprint import pformat

PROLOGUE = """#!/usr/bin/env python

import requests

session = requests.Session()

"""

REQUEST_TEMPLATE = """
headers_{idx} = {headers}
data_{idx} = {data}

response_{idx} = session.{method}(
    url={url},
    headers=headers_{idx},
    data=data_{idx}
)

#print(response_{idx}.content)
"""

def generate_request(http_message, index):
    req_info = http_message.req_info
    req_data = http_message.req_data
    headers = pformat(dict(header.split(': ', 1) for header in req_info.getHeaders()[1:]))
    method = req_info.getMethod().lower()
    url = pformat(str(req_info.getUrl()))
    data = pformat(bytearray(req_data[req_info.getBodyOffset():]))
    return REQUEST_TEMPLATE.format(
        headers=headers,
        data=data,
        url=url,
        method=method,
        idx=index
    )
    

def generate_script(messages):
    snippets = [PROLOGUE]
    for idx, message in enumerate(messages):
        snippets.append(generate_request(message, idx))
    return "".join(snippets)
