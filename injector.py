# injector.py
import requests

def send(url, method='GET', params=None, data=None, headers=None, timeout=8):
    if method == 'GET':
        return requests.get(url, params=params, headers=headers, timeout=timeout)
    return requests.post(url, params=params, data=data, headers=headers, timeout=timeout)

def send_with_param_name(url, payload_name, method='GET', extra_data=None, headers=None, timeout=8):
    # payload_name used as parameter name
    params = {payload_name: (extra_data or '1')}
    return send(url, method=method, params=params, data=extra_data, headers=headers, timeout=timeout)
