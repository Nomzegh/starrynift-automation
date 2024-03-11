import time

from requests.sessions import Session
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.providers.rpc import HTTPProvider
from eth_account.messages import encode_defunct

from utils.utils import current_time
from config import transactions_break_time, gas_price


def create_web3_with_proxy(rpc_endpoint, proxy=None):
    if proxy is None:
        return Web3(Web3.HTTPProvider(rpc_endpoint))

    proxy_settings = {
        "http": proxy,
        "https": proxy,
    }

    session = Session()
    session.proxies = proxy_settings

    custom_provider = HTTPProvider(rpc_endpoint, session=session)
    web3 = Web3(custom_provider)
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    return web3


def initialize_account(private_key):
    web3 = Web3()

    return web3.eth.account.from_key(private_key)


def estimate_gas_and_send(web3, tx, private_key, tx_name):
    tx["gas"] = int(web3.eth.estimate_gas(tx))
    signed_txn = web3.eth.account.sign_transaction(tx, private_key)
    transaction_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction).hex()

    print(f"{current_time()} | Waiting {tx_name} to complete...")
    receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
    if receipt.status != 1:
        print(f"{current_time()} | Transaction {transaction_hash} failed!")
        time.sleep(transactions_break_time)
        return

    print(f"{current_time()} | {tx_name} hash: {transaction_hash}")
    time.sleep(transactions_break_time)

    return transaction_hash


def create_transaction(web3, private_key, tx_name, to, value, data):
    account = initialize_account(private_key)
    tx = {
        "from": account.address,
        "to": web3.to_checksum_address(to),
        "value": value,
        "nonce": web3.eth.get_transaction_count(account.address),
        "gasPrice": web3.to_wei(gas_price, "gwei"),
        "chainId": 56,
        "data": data,
    }
    return estimate_gas_and_send(web3, tx, private_key, tx_name)


def sign_with_key(message_to_sign, private_key):  # returns signature
    account = initialize_account(private_key)
    signature = account.sign_message(
        encode_defunct(text=message_to_sign)
    ).signature.hex()

    return signature
