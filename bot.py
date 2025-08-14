from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout,
    BasicAuth
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from nacl.signing import SigningKey
from dotenv import load_dotenv
from datetime import datetime
from colorama import *
import asyncio, random, base64, json, re, os, pytz

load_dotenv()

wib = pytz.timezone('Asia/Jakarta')

class FastSet:
    def __init__(self) -> None:
        self.HEADERS = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Host": "wallet.fastset.xyz",
            "Origin": "https://wallet.fastset.xyz",
            "Referer": "https://wallet.fastset.xyz/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://wallet.fastset.xyz"
        self.SET_TOKEN = {
            "token_name": "SET",
            "token_ticker": "SET",
            "drip_value": 98686
        }
        self.USDC_TOKEN = {
            "token_name": "USDC",
            "token_ticker": "USDC",
            "decimals": 6,
            "drip_value": 1000,
            "token_id": "ReFosxqpCeJTBuJXJOSoAFE8F4+fXpftTJBYs8qAaeI="
        }
        self.ETH_TOKEN = {
            "token_name": "ETH",
            "token_ticker": "ETH",
            "decimals": 18,
            "drip_value": 3.14,
            "token_id": "webWlA8UWwxnPc+awV0isStdDwYyynDf+eoh3ezEzWc="
        }
        self.SOL_TOKEN = {
            "token_name": "SOL",
            "token_ticker": "SOL",
            "decimals": 9,
            "drip_value": 100,
            "token_id": "2EJhDfYD4V39bKTVgJUhEd0LAs3VUAfEiGRucXc9eHU="
        }
        self.BTC_TOKEN = {
            "token_name": "BTC",
            "token_ticker": "BTC",
            "decimals": 8,
            "drip_value": 1,
            "token_id": "/NHeobovw7GeS14wseW3RmvFRQIojkfWEGG+0HaIPtE="
        }
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.transfer_count = 0
        self.set_amount = float(os.getenv("SET_AMOUNT"))
        self.usdc_amount = float(os.getenv("USDC_AMOUNT"))
        self.eth_amount = float(os.getenv("ETH_AMOUNT"))
        self.sol_amount = float(os.getenv("SOL_AMOUNT"))
        self.btc_amount = float(os.getenv("BTC_AMOUNT"))
        self.min_delay = int(os.getenv("MIN_DELAY"))
        self.max_delay = int(os.getenv("MAX_DELAY"))

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}FastSet Wallet {Fore.BLUE + Style.BRIGHT}Auto BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self):
        filename = "proxy.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def build_proxy_config(self, proxy=None):
        if not proxy:
            return None, None, None

        if proxy.startswith("socks"):
            connector = ProxyConnector.from_url(proxy)
            return connector, None, None

        elif proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = BasicAuth(username, password)
                return None, clean_url, auth
            else:
                return None, proxy, None

        raise Exception("Unsupported Proxy Type.")

    def polymod(self, values):
        gens = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
        chk = 1
        for v in values:
            b = (chk >> 25) & 0xff
            chk = ((chk & 0x1ffffff) << 5) ^ v
            for i in range(5):
                if ((b >> i) & 1):
                    chk ^= gens[i]
        return chk

    def hrp_expand(self, hrp):
        return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

    def create_checksum(self, hrp, data):
        values = self.hrp_expand(hrp) + data
        polymod_result = self.polymod(values + [0, 0, 0, 0, 0, 0]) ^ 0x2bc830a3
        return [(polymod_result >> 5 * (5 - i)) & 31 for i in range(6)]

    def bech32m_encode(self, hrp, data):
        charset = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
        combined = data + self.create_checksum(hrp, data)
        return hrp + "1" + "".join([charset[d] for d in combined])

    def convertbits(self, data, frombits, tobits, pad=True):
        acc = 0
        bits = 0
        ret = []
        maxv = (1 << tobits) - 1
        for value in data:
            acc = (acc << frombits) | value
            bits += frombits
            while bits >= tobits:
                bits -= tobits
                ret.append((acc >> bits) & maxv)
        if pad:
            if bits:
                ret.append((acc << (tobits - bits)) & maxv)
        elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
            return None
        return ret
    
    def generate_account_data(self, account):
        try:
            seed_bytes = bytes.fromhex(account)

            signing_key = SigningKey(seed_bytes)
            verify_key = signing_key.verify_key
            pub_bytes = verify_key.encode()

            address_base64 = base64.b64encode(pub_bytes).decode()

            words = self.convertbits(pub_bytes, 8, 5)
            address_bech32m = self.bech32m_encode("set", words)

            keypair_bytes = seed_bytes + pub_bytes
            keypair_base64 = base64.b64encode(keypair_bytes).decode()

            return address_base64, address_bech32m, keypair_base64
        except Exception as e:
            return None, None, None
        
    def generate_recipient_data(self):
        try:
            account = os.urandom(32).hex()
            seed_bytes = bytes.fromhex(account)

            signing_key = SigningKey(seed_bytes)
            verify_key = signing_key.verify_key
            pub_bytes = verify_key.encode()

            address_base64 = base64.b64encode(pub_bytes).decode()

            words = self.convertbits(pub_bytes, 8, 5)
            address_bech32m = self.bech32m_encode("set", words)

            return address_base64, address_bech32m
        except Exception as e:
            return None, None
        
    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception as e:
            return None
         
    async def print_timer(self):
        for remaining in range(random.randint(self.min_delay, self.max_delay), 0, -1):
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {remaining} {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Seconds For Next Tx...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)

    def print_question(self):
        while True:
            try:
                print(f"{Fore.GREEN + Style.BRIGHT}Select Option:{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}1. Request Drip{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Make Transfer{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run All Features{Style.RESET_ALL}")
                option = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if option in [1, 2, 3]:
                    option_type = (
                        "Request Drip" if option == 1 else 
                        "Make Transfer" if option == 2 else 
                        "Run All Features"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{option_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2, or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2, or 3).{Style.RESET_ALL}")

        if option in [2, 3]:
            while True:
                try:
                    transfer_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}Transfer Count For Each Wallet -> {Style.RESET_ALL}").strip())
                    if transfer_count > 0:
                        self.transfer_count = transfer_count
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Transfer Count must be > 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2]:
                    proxy_type = "With" if choose == 2 else "Without"
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        rotate = False
        if choose == 1:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return option, choose, rotate
    
    async def check_connection(self, proxy_url=None):
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(url="https://api.ipify.org?format=json", proxy=proxy, proxy_auth=proxy_auth) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
        
        return None
            
    async def get_account_info(self, sender: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/getAccountInfo"
        data = json.dumps({"sender":sender})
        headers = {
            **self.HEADERS,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        resp_text = await response.text()
                        return json.loads(resp_text)
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Message  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch Token Balances Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
            
    async def drip_balance(self, sender: str, amount: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/dripBalance"
        data = json.dumps({
            "sender":sender,
            "info":{
                "recipient":sender,
                "amount":amount
            }
        })
        headers = {
            **self.HEADERS,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        resp_text = await response.text()
                        return json.loads(resp_text)
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
            
    async def drip_token(self, sender: str, amount: str, token_id, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/dripToken"
        data = json.dumps({
            "sender":sender,
            "info":{
                "recipient":sender,
                "amount":amount,
                "tokenId":token_id
            }
        })
        headers = {
            **self.HEADERS,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        resp_text = await response.text()
                        return json.loads(resp_text)
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
            
    async def transfer_balance(self, sender: str, keypair: str, nonce: str, recipient: str, amount: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/transferBalance"
        data = json.dumps({
            "sender":sender, 
            "key":keypair,
            "nextNonce":nonce, 
            "transferInfo":{
                "recipient":recipient, 
                "amount":amount
            }
        })
        headers = {
            **self.HEADERS,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        resp_text = await response.text()
                        return json.loads(resp_text)
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
            
    async def transfer_token(self, sender: str, keypair: str, nonce: str, token_id: str, recipient: str, amount: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/transferToken"
        data = json.dumps({
            "sender":sender, 
            "key":keypair,
            "nextNonce":nonce, 
            "transferInfo":{
                "tokenId":token_id, 
                "recipient":recipient, 
                "amount":amount
            }
        })
        headers = {
            **self.HEADERS,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        resp_text = await response.text()
                        return json.loads(resp_text)
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
    
    async def process_check_connection(self, sender: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(sender) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy)
            if not is_valid:
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(sender)
                    await asyncio.sleep(1)
                    continue
                
                return False
            
            return True
    
    async def process_option_1(self, sender: str, proxy=None):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Req Drips :{Style.RESET_ALL}                                   ")
        token_list = [
            self.SET_TOKEN,
            self.USDC_TOKEN,
            self.ETH_TOKEN,
            self.SOL_TOKEN,
            self.BTC_TOKEN
        ]

        for token in token_list:
            token_name = token["token_name"]
            drip_value = token["drip_value"]

            self.log(
                f"{Fore.GREEN+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{token_name}{Style.RESET_ALL}                                   "
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Amount   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {drip_value} {token_name} {Style.RESET_ALL}"
            )

            if token_name == "SET":
                amount_raw = str(drip_value)
                
                drip = await self.drip_balance(sender, amount_raw, proxy_url=proxy)
                if drip:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                    )

            else:
                decimals = token["decimals"]
                token_id = token["token_id"]
                amount_raw = str(int(drip_value * (10 ** decimals)))

                drip = await self.drip_token(sender, amount_raw, token_id, proxy_url=proxy)
                if drip:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                    )

            await self.print_timer()

    async def process_option_2(self, sender: str, keypair: str, proxy=None):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Transfer  :{Style.RESET_ALL}                                   ")
        for i in range(self.transfer_count):
            self.log(
                f"{Fore.GREEN+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{i+1}{Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT} Of {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{self.transfer_count}{Style.RESET_ALL}                                   "
            )

            account = await self.get_account_info(sender, proxy)
            if not account: continue

            token_map = {
                self.USDC_TOKEN["token_id"]: self.USDC_TOKEN,
                self.ETH_TOKEN["token_id"]: self.ETH_TOKEN,
                self.SOL_TOKEN["token_id"]: self.SOL_TOKEN,
                self.BTC_TOKEN["token_id"]: self.BTC_TOKEN,
            }

            balance = account["balance"]
            nonce = account["nextNonce"]

            token_balances = {
                token_map[token_id]["token_ticker"]: int(raw_balance) / (10 ** token_map[token_id]["decimals"])
                for token_id, raw_balance in account["tokenBalances"].items()
                if token_id in token_map
            }

            available_tokens = ["SET"] + list(token_balances.keys())

            token_name = random.choice(available_tokens)
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Token Use:{Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT} {token_name} {Style.RESET_ALL}"
            )

            recepient_base64, recepient_bech32m = self.generate_recipient_data()
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Recipinet:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {recepient_bech32m} {Style.RESET_ALL}"
            )

            if token_name == "SET":
                token_balance = int(balance)
                amount_input = self.set_amount

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Balance  :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {token_balance} {token_name} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Amount   :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {amount_input} {token_name} {Style.RESET_ALL}"
                )

                if amount_input > token_balance:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}   Message  :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Insufficient {token_name} Token Balance {Style.RESET_ALL}"
                    )
                    continue

                amount_raw = str(int(amount_input))

                transfer = await self.transfer_balance(sender, keypair, nonce, recepient_base64, amount_raw, proxy_url=proxy)
                if transfer:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                    )

            else:
                token_info = getattr(self, f"{token_name}_TOKEN")
                token_balance = token_balances[token_name]
                decimals = token_info["decimals"]
                token_id = token_info["token_id"]

                if token_name == "USDC":
                    amount_input = self.usdc_amount
                elif token_name == "ETH":
                    amount_input = self.eth_amount
                elif token_name == "SOL":
                    amount_input = self.sol_amount
                elif token_name == "BTC":
                    amount_input = self.btc_amount

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Balance  :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {token_balance} {token_name} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Amount   :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {amount_input} {token_name} {Style.RESET_ALL}"
                )

                if amount_input > token_balance:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}   Message  :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Insufficient {token_name} Token Balance {Style.RESET_ALL}"
                    )
                    continue

                amount_raw = str(int(amount_input * (10 ** decimals)))

                transfer = await self.transfer_token(sender, keypair, nonce, token_id, recepient_base64, amount_raw, proxy_url=proxy)
                if transfer:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                    )

            await self.print_timer()

    async def process_accounts(self, sender: str, keypair: str, option: int, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(sender, use_proxy, rotate_proxy)
        if is_valid:
            proxy = self.get_next_proxy_for_account(sender) if use_proxy else None

            if option == 1:
                await self.process_option_1(sender, proxy)

            elif option == 2:
                await self.process_option_2(sender, keypair, proxy)

            elif option == 3:
                await self.process_option_1(sender, proxy)
                await self.process_option_2(sender, keypair, proxy)
            
    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            option, proxy_choice, rotate_proxy = self.print_question()

            use_proxy = True if proxy_choice == 1 else False

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies()

                separator = "=" * 25
                for account in accounts:
                    if account:
                        sender, address, keypair = self.generate_account_data(account)
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if not sender or not address or not keypair:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}Status    :{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Invalid Private Key or Library Version Not Supported {Style.RESET_ALL}"
                            )
                            continue
                        
                        await self.process_accounts(sender, keypair, option, use_proxy, rotate_proxy)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*72)
                
                delay = 12 * 60 * 60
                while delay > 0:
                    formatted_time = self.format_seconds(delay)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed...{Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    await asyncio.sleep(1)
                    delay -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = FastSet()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] FastSet Wallet - BOT{Style.RESET_ALL}                                       "                              
        )