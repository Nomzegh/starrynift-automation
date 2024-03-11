import time
import json

from utils.web3_utils import initialize_account
from utils.starrynift_utils import (
    login_request,
    mint_citizencard,
    checkin,
    online_ping,
    check_stats,
    follow,
)
from utils.utils import return_accounts_array, load_keys_with_proxies


def process_accounts(func):
    accounts_array = return_accounts_array()
    for account_info in accounts_array:
        try:
            account_dict = json.loads(account_info)
            func(account_dict)
        except Exception as e:
            error_message = f"Error for address: {initialize_account(account_dict['private_key']).address} | Error: {e}\n"
            print(error_message)
            time.sleep(3)
            with open("./data/fail_logs.txt", "a") as log_file:
                log_file.write(error_message + f" ")


if __name__ == "__main__":
    choice = int(
        input(
            "\n----------------------"
            "\n1: Sign in (creates account{} in accounts.txt)"
            "\n2: Citizen card mint"
            "\n3: Daily check in (TX + Verify)"
            "\n4: Online ping"
            "\n5: Check profile info"
            "\n6: Follow profile"
            "\n----------------------"
            "\nChoice: "
        )
    )

    transaction_functions = {
        1: lambda: [login_request(key, proxy) for key, proxy in zip(*load_keys_with_proxies())],
        2: lambda: process_accounts(mint_citizencard),
        3: lambda: process_accounts(checkin),
        4: lambda: [process_accounts(online_ping) or time.sleep(30) for _ in range(22)],
        5: lambda: process_accounts(check_stats),
        6: lambda: process_accounts(follow),
    }

    if choice in transaction_functions:
        transaction_functions[choice]()
    else:
        print("Wrong choice number. 1 | 2 | 3 ...")
