import requests
from typing import Dict, Optional


def send_get(url: str, params: Dict[str, str], timeout: int = 8):
    return requests.get(url, params=params, timeout=timeout)


def send_post(url: str, data: Dict[str, str], timeout: int = 8):
    return requests.post(url, data=data, timeout=timeout)


def send_with_param_name(url: str, payload_name: str, method: str = "GET", timeout: int = 8):
    params = {payload_name: "1"}

    if method.upper() == "GET":
        return requests.get(url, params=params, timeout=timeout)

    # POST with payload as parameter name
    return requests.post(url, params=params, data={"x": "1"}, timeout=timeout)
