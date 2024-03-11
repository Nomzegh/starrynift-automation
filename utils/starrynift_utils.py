from eth_abi import encode

from utils.web3_utils import (
    initialize_account,
    sign_with_key,
    create_web3_with_proxy,
    create_transaction,
)
from utils.requests_utils import create_session
from utils.utils import current_time, add_access_token_to_file

from config import RPC, id_to_follow


def get_login_message(private_key, session):  # returns challenge message
    account = initialize_account(private_key)
    params = {
        "address": account.address,
    }
    login_message = session.get(
        url="https://api.starrynift.art/api-v2/starryverse/auth/wallet/challenge",
        params=params,
    ).json()

    return login_message["message"]


def login_request(
    private_key, proxy
):  # logs in and creates account dict in accounts.txt
    session = create_session(proxy)
    account = initialize_account(private_key)
    message = get_login_message(private_key=private_key, session=session)
    signature = sign_with_key(private_key=private_key, message_to_sign=message)

    json_data = {
        "address": account.address,
        "signature": signature,
        "referralCode": "2XSzXVUBO6",
        "referralSource": 0,
    }

    response = session.post(
        "https://api.starrynift.art/api-v2/starryverse/auth/wallet/evm/login",
        json=json_data,
    ).json()
    access_token = response["token"]
    user_agent = session.headers["User-Agent"]
    add_access_token_to_file(private_key, access_token, proxy, user_agent)
    print(f"{current_time()} | {account.address} | Log in Successful ")

    return access_token


def checkin(account_dict):  # sends checkin tx and verifies with checkin_verify()
    session = create_session(account_dict["proxies"])
    session.headers.update({"User-Agent": account_dict["user_agent"]})
    access_token = account_dict["access_token"]
    web3 = create_web3_with_proxy(RPC, account_dict["proxies"])
    web3_account = initialize_account(account_dict["private_key"])

    tx_hash = create_transaction(
        web3=web3,
        private_key=web3_account.key,
        tx_name="Checkin Transaction",
        to="0xE3bA0072d1da98269133852fba1795419D72BaF4",
        value=0,
        data="0x9e4cda43",
    )

    checkin_verify(
        session=session,
        tx_hash=tx_hash,
        access_token=access_token,
    )


def checkin_verify(
    session, tx_hash, access_token
):  # verifies tx_hash received from checkin()
    session.headers.update({"Authorization": f"Bearer {access_token}"})

    status = session.post(
        "https://api.starrynift.art/api-v2/webhook/confirm/daily-checkin/checkin",
        json={
            "txHash": tx_hash,
        },
    ).json()

    print(f"{current_time()} | Checkin status: {status}")
    return status


def mint_citizencard(
    account_dict,
):  # sends mint tx and verifies tx_hash with confirm_citizencard_mint()
    proxy = account_dict["proxies"]
    access_token = account_dict["access_token"]
    account = initialize_account(account_dict["private_key"])

    web3 = create_web3_with_proxy(RPC, proxy=proxy)
    session = create_session(proxy)
    session.headers.update(
        {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": account_dict["user_agent"],
        }
    )
    response = session.post(
        "https://api.starrynift.art/api-v2/citizenship/citizenship-card/sign",
        json={
            "category": 1,
        },
    ).json()
    mint_signature = response["signature"]
    params = [
        account.address,
        1,
        bytes.fromhex(mint_signature[2:]),
    ]
    encoded_params = encode(["(address,uint256,bytes)"], [params])
    tx_data = "0xf75e0384" + encoded_params.hex()

    tx_hash = create_transaction(
        web3=web3,
        private_key=account.key,
        tx_name="Citizen Card Mint TX",
        to="0xc92df682a8dc28717c92d7b5832376e6ac15a90d",
        value=0,
        data=tx_data,
    )
    if tx_hash:
        confirm_citizencard_mint(account=account, session=session, tx_hash=tx_hash)


def confirm_citizencard_mint(
    account, session, tx_hash
):  # verifies tx_hash received from mint_citizencard()
    response = session.post(
        "https://api.starrynift.art/api-v2/webhook/confirm/citizenship/mint",
        json={
            "txHash": tx_hash,
        },
    ).json()
    print(f"{current_time()} | {account.address} | Mint Confirm Status: {response}")


def online_ping(account_dict):  # sends a request and returns .json with online time
    starrynift_account = account_dict

    access_token = starrynift_account["access_token"]
    account = initialize_account(starrynift_account["private_key"])

    session = create_session(starrynift_account["proxies"])
    session.headers.update(
        {
            "Accept": "*/*",
            "Authorization": f"Bearer {access_token}",
            "User-Agent": starrynift_account["user_agent"],
        }
    )

    response = session.get("https://api.starrynift.art/api-v2/space/online/ping").json()

    print(
        f"{current_time()} | Completed: {response['completed']} | {account.address} | Online for: {response['minutes']}m ({response['seconds']}s) | Active days: {response['days']}"
    )


def check_stats(
    account_dict,
):  # sends a request and returns profile info: level, points, top
    session = create_session(account_dict["proxies"])
    session.headers.update(
        {
            "Accept": "*/*",
            "Authorization": f"Bearer {account_dict['access_token']}",
            "User-Agent": account_dict["user_agent"],
        }
    )
    response = session.get(
        "https://api.starrynift.art/api-v2/starryverse/achievement/ranking"
    ).json()
    resp = response["my"]
    print(
        f"{current_time()} | {resp['address']} | Level: {resp['level']} ({resp['points']} points) | Top: {resp['index']} "
    )


def follow(account_dict):  # sends follow request and returns follow status
    session = create_session(account_dict["proxies"])
    session.headers.update(
        {
            "Accept": "*/*",
            "Authorization": f"Bearer {account_dict['access_token']}",
            "User-Agent": account_dict["user_agent"],
        }
    )
    response = session.post(
        "https://api.starrynift.art/api-v2/starryverse/user/follow",
        json={
            "userId": id_to_follow,
        },
    ).json()

    print(
        f"{current_time()} | {initialize_account(account_dict['private_key']).address} | Follow status: {response}"
    )
