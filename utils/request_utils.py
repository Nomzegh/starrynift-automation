import requests
from requests.sessions import Session
from fake_useragent import UserAgent

from utils.utils import extract_ip_from_proxy


def create_session(proxy=None, check_proxy=False): # True if check needed
    session = Session()
    session.headers.update(
        {
            "User-Agent": UserAgent().random,
            "Accept": "application/json, text/plain, */*",
            "Connection": "keep-alive",
            "Origin": "https://starrynift.art",
            "Referer": "https://starrynift.art/",
        }
    )

    if proxy:
        session.proxies = {"http": proxy, "https": proxy}

    if check_proxy and proxy:
        try:
            proxy_ip = extract_ip_from_proxy(proxy)
            actual_ip = session.get("https://api.ipify.org").text
            if actual_ip != proxy_ip:
                raise Exception(
                    f"Error: Proxy IP ({proxy_ip}) does not match actual IP ({actual_ip}). Stopping script."
                )

            else:
                print(f"Proxy check passed: {actual_ip}")
        except requests.RequestException as e:
            raise Exception(f"Error during proxy check: {e}")

    return session
