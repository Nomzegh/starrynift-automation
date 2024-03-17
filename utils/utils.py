import time
import json
from datetime import datetime, timedelta


def current_time():
    cur_time = time.strftime("%Y-%m-%d %H:%M:%S")[:-3]
    return cur_time


def add_access_token_to_file(private_key, access_token, proxy, user_agent):
    valid_until = datetime.now() + timedelta(days=6)
    valid_until_str = valid_until.strftime("%Y-%m-%d")
    updated = False

    accounts_data = []
    try:
        with open("./data/accounts.txt", "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                try:
                    account = json.loads(line)
                    if account["private_key"] == private_key:
                        account["valid_until"] = valid_until_str
                        account["access_token"] = access_token
                        updated = True
                except json.JSONDecodeError:
                    continue
                accounts_data.append(account)
    except FileNotFoundError:
        pass

    if not updated:
        accounts_data.append(
            {
                "private_key": private_key,
                "valid_until": valid_until_str,
                "proxies": proxy,
                "access_token": access_token,
                "user_agent": user_agent,
            }
        )

    with open("./data/accounts.txt", "w") as file:
        for account in accounts_data:
            file.write(json.dumps(account) + "\n")


def extract_ip_from_proxy(proxy):
    if proxy.startswith("http://"):
        proxy = proxy[7:]
    elif proxy.startswith("https://"):
        proxy = proxy[8:]

    at_split = proxy.split("@")[-1]
    ip = at_split.split(":")[0]

    return ip


def load_keys_with_proxies():
    private_keys = []
    proxies = []

    with open("./data/keys.txt", "r") as f:
        for line in f:
            line = line.strip()
            private_keys.append(line)

    with open("./data/proxies.txt", "r") as p:
        for proxy in p:
            proxy = proxy.strip()
            proxies.append(proxy)

    return private_keys, proxies


def return_accounts_array():
    with open("./data/accounts.txt", "r") as file:
        accounts_data = file.readlines()
    return accounts_data
