from curl_cffi import requests
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, json, os, pytz, logging

wib = pytz.timezone('Asia/Jakarta')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DDAI:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://app.ddai.network",
            "Referer": "https://app.ddai.network/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://auth.ddai.network"
        self.PAGE_URL = "https://app.ddai.network"
        self.SITE_KEY = "0x4AAAAAABdw7Ezbqw4v6Kr1"
        self.CAPTCHA_KEY = None
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.captcha_tokens = {}
        self.password = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(f"""
{Fore.CYAN + Style.BRIGHT}╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║  {Fore.YELLOW + Style.BRIGHT}🔧 DDAI NETWORK - TOKEN SETUP WIZARD 🔧{Fore.CYAN + Style.BRIGHT}                     ║
║                                                                  ║
║  {Fore.GREEN + Style.BRIGHT}🚀 Advanced Multi-Account Token Generator 🚀{Fore.CYAN + Style.BRIGHT}                ║
║                                                                  ║
║  {Fore.MAGENTA + Style.BRIGHT}⚡ Features:{Fore.CYAN + Style.BRIGHT}                                                ║
║    {Fore.WHITE + Style.BRIGHT}🔐 CloudFlare Captcha Solver (2captcha){Fore.CYAN + Style.BRIGHT}                   ║
║    {Fore.WHITE + Style.BRIGHT}⚡ Parallel Processing (3x faster){Fore.CYAN + Style.BRIGHT}                        ║
║    {Fore.WHITE + Style.BRIGHT}🌐 Multi-Proxy Support{Fore.CYAN + Style.BRIGHT}                                    ║
║    {Fore.WHITE + Style.BRIGHT}🛡️ Smart Error Recovery{Fore.CYAN + Style.BRIGHT}                                   ║
║    {Fore.WHITE + Style.BRIGHT}💾 Auto Token Management{Fore.CYAN + Style.BRIGHT}                                  ║
║                                                                  ║
║  {Fore.BLUE + Style.BRIGHT}👨‍💻 Original Creator: vonssy{Fore.CYAN + Style.BRIGHT}                                  ║
║  {Fore.BLUE + Style.BRIGHT}🔧 Enhanced by: jack0z{Fore.CYAN + Style.BRIGHT}                                       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.YELLOW + Style.BRIGHT}💡 TIP: Run this setup first, then use bot.py to start farming! 💡{Style.RESET_ALL}
        """)

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "accounts.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
        
    def save_tokens(self, new_accounts):
        filename = "tokens.json"
        try:
            existing_accounts = []
            
            # Try to load existing tokens, but handle invalid JSON gracefully
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                try:
                    with open(filename, 'r') as file:
                        existing_accounts = json.load(file)
                        if not isinstance(existing_accounts, list):
                            existing_accounts = []
                except json.JSONDecodeError:
                    self.log(f"{Fore.YELLOW + Style.BRIGHT}⚠️ tokens.json contains invalid JSON, creating new file{Style.RESET_ALL}")
                    existing_accounts = []
                except Exception as e:
                    self.log(f"{Fore.YELLOW + Style.BRIGHT}⚠️ Could not read tokens.json: {e}, creating new file{Style.RESET_ALL}")
                    existing_accounts = []

            # Merge existing and new accounts
            account_dict = {acc["Email"]: acc for acc in existing_accounts}

            for new_acc in new_accounts:
                account_dict[new_acc["Email"]] = new_acc

            updated_accounts = list(account_dict.values())

            # Save to file
            with open(filename, 'w') as file:
                json.dump(updated_accounts, file, indent=4)
                
            self.log(f"{Fore.GREEN + Style.BRIGHT}💾 Successfully saved {len(new_accounts)} token(s) to {filename}{Style.RESET_ALL}")
            return True

        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Failed to save tokens: {e}{Style.RESET_ALL}")
            return False
        
    def load_2captcha_key(self):
        try:
            with open("2captcha_key.txt", 'r') as file:
                captcha_key = file.read().strip()

            return captcha_key
        except Exception as e:
            return None

    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                response = await asyncio.to_thread(requests.get, "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text")
                response.raise_for_status()
                content = response.text
                with open(filename, 'w') as f:
                    f.write(content)
                self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else:
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

    def get_next_proxy_for_account(self, user_id):
        if user_id not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[user_id] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[user_id]

    def rotate_proxy_for_account(self, user_id):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[user_id] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def mask_account(self, account):
        if '@' in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"

    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Free Proxyscrape Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Free Proxyscrape" if choose == 1 else 
                        "With Private" if choose == 2 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

    def print_processing_question(self):
        while True:
            try:
                print(f"\n{Fore.WHITE + Style.BRIGHT}Processing Mode:{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}1. Sequential (Original - Most Reliable){Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Parallel (Faster but may have captcha issues){Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2]:
                    processing_type = "Sequential" if choose == 1 else "Parallel"
                    print(f"{Fore.GREEN + Style.BRIGHT}{processing_type} Processing Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")
    
    async def solve_cf_turnstile(self, email: str, proxy=None, retries=5):
        """Solve CloudFlare Turnstile captcha using 2captcha - EXACT WORKING VERSION"""
        if self.CAPTCHA_KEY is None:
            self.log(f"{Fore.RED + Style.BRIGHT}No 2captcha API key available{Style.RESET_ALL}")
            return False
            
        for attempt in range(retries):
            try:
                self.log(f"{Fore.MAGENTA + Style.BRIGHT}🔐 Solving captcha for {self.mask_account(email)} (attempt {attempt + 1}/{retries}){Style.RESET_ALL}")
                
                # Submit captcha to 2captcha
                url = f"http://2captcha.com/in.php?key={self.CAPTCHA_KEY}&method=turnstile&sitekey={self.SITE_KEY}&pageurl={self.PAGE_URL}"
                response = await asyncio.to_thread(requests.get, url=url, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)
                response.raise_for_status()
                result = response.text

                if 'OK|' not in result:
                    self.log(f"{Fore.YELLOW + Style.BRIGHT}Failed to submit captcha: {result}{Style.RESET_ALL}")
                    await asyncio.sleep(5)
                    continue

                request_id = result.split('|')[1]
                self.log(
                    f"{Fore.MAGENTA + Style.BRIGHT}    >{Style.RESET_ALL}"
                    f"{Fore.BLUE + Style.BRIGHT} Captcha submitted, Req Id: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{request_id}{Style.RESET_ALL}"
                )

                # Poll for result
                for poll_attempt in range(30):  # 30 attempts, 5 sec each = 2.5 min max
                    await asyncio.sleep(5)
                    
                    res_url = f"http://2captcha.com/res.php?key={self.CAPTCHA_KEY}&action=get&id={request_id}"
                    res_response = await asyncio.to_thread(requests.get, url=res_url, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)
                    res_response.raise_for_status()
                    res_result = res_response.text

                    if 'OK|' in res_result:
                        captcha_token = res_result.split('|')[1]
                        self.captcha_tokens[email] = captcha_token
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}    >{Style.RESET_ALL}"
                            f"{Fore.BLUE + Style.BRIGHT} Status: {Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT}✅ Captcha solved successfully{Style.RESET_ALL}"
                        )
                        return True
                    elif res_result == "CAPCHA_NOT_READY":
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}    >{Style.RESET_ALL}"
                            f"{Fore.BLUE + Style.BRIGHT} Status: {Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT}⏳ Captcha not ready, waiting... ({poll_attempt + 1}/30){Style.RESET_ALL}"
                        )
                        continue
                    else:
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}    >{Style.RESET_ALL}"
                            f"{Fore.BLUE + Style.BRIGHT} Status: {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}❌ Captcha solving failed: {res_result}{Style.RESET_ALL}"
                        )
                        break

            except Exception as e:
                self.log(f"{Fore.RED + Style.BRIGHT}Error solving captcha for {self.mask_account(email)} (attempt {attempt + 1}): {e}{Style.RESET_ALL}")
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

        self.log(f"{Fore.RED + Style.BRIGHT}❌ Failed to solve captcha for {self.mask_account(email)} after {retries} attempts{Style.RESET_ALL}")
        return False

    async def auth_login(self, email: str, proxy=None, retries=3):
        """Login with captcha token - EXACT WORKING VERSION"""
        # Get captcha token (should be solved already)
        captcha_token = self.captcha_tokens.get(email, "")
        
        url = f"{self.BASE_API}/login"
        data = json.dumps({
            "email": email, 
            "password": self.password[email], 
            "captchaToken": captcha_token
        })
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }

        self.log(f"{Fore.CYAN + Style.BRIGHT}🔑 Attempting login for {self.mask_account(email)}{Style.RESET_ALL}")
        
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(
                    requests.post, 
                    url=url, 
                    headers=headers, 
                    data=data, 
                    proxy=proxy, 
                    timeout=60, 
                    impersonate="chrome110", 
                    verify=False
                )
                
                self.log(f"{Fore.CYAN + Style.BRIGHT}Login response status for {self.mask_account(email)}: {response.status_code}{Style.RESET_ALL}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "success":
                        login_data = result.get("data", {})
                        access_token = login_data.get("accessToken")
                        refresh_token = login_data.get("refreshToken")
                        
                        if access_token and refresh_token:
                            self.log(f"{Fore.GREEN + Style.BRIGHT}✅ Successfully logged in {self.mask_account(email)}{Style.RESET_ALL}")
                            return access_token, refresh_token
                        else:
                            self.log(f"{Fore.RED + Style.BRIGHT}Missing tokens in login response for {self.mask_account(email)}{Style.RESET_ALL}")
                    else:
                        self.log(f"{Fore.RED + Style.BRIGHT}Login failed for {self.mask_account(email)}: {result.get('message', result)}{Style.RESET_ALL}")
                elif response.status_code == 403:
                    self.log(f"{Fore.RED + Style.BRIGHT}Login blocked for {self.mask_account(email)} - captcha may have failed{Style.RESET_ALL}")
                else:
                    self.log(f"{Fore.RED + Style.BRIGHT}Login failed for {self.mask_account(email)}: {response.status_code}{Style.RESET_ALL}")
                    
            except Exception as e:
                self.log(f"{Fore.RED + Style.BRIGHT}Error in login attempt {attempt + 1} for {self.mask_account(email)}: {e}{Style.RESET_ALL}")
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    
        return None, None
        
    async def process_accounts(self, email: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(email) if use_proxy else None
    
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}Proxy  :{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {proxy} {Style.RESET_ALL}"
        )

        self.log(f"{Fore.CYAN + Style.BRIGHT}Captcha:{Style.RESET_ALL}")

        # Use the WORKING captcha solver
        cf_solved = await self.solve_cf_turnstile(email, proxy)
        if not cf_solved:
            return
        
        # Use the WORKING login method
        access_token, refresh_token = await self.auth_login(email, proxy)
        if access_token and refresh_token:
            save_success = self.save_tokens([{"Email":email, "accessToken":access_token, "refreshToken":refresh_token}])
            
            if save_success:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Status :{Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT} ✅ Token Have Been Saved Successfully {Style.RESET_ALL}"
                )
            else:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Status :{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} ❌ Failed To Save Token {Style.RESET_ALL}"
                )

    async def process_single_account(self, account, use_proxy, idx, total_accounts, semaphore):
        """Process a single account with semaphore for rate limiting"""
        async with semaphore:
            email = account["Email"]
            password = account["Password"]
            
            self.log(
                f"{Fore.CYAN + Style.BRIGHT}=========================[{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT}Of{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {total_accounts} {Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT}]========================={Style.RESET_ALL}"
            )

            if not "@" in email or not password:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Invalid Account Data {Style.RESET_ALL}"
                )
                return None

            self.log(
                f"{Fore.CYAN + Style.BRIGHT}Account:{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(email)} {Style.RESET_ALL}"
            )

            self.password[email] = password

            # Use the original process_accounts logic
            await self.process_accounts(email, use_proxy)
            
            # Add delay between accounts (but smaller than original since we're parallel)
            await asyncio.sleep(1)
            
            return True

    async def setup_tokens_parallel(self, accounts, use_proxy):
        """Setup tokens for accounts in parallel"""
        # Create semaphore to limit concurrent requests (avoid overwhelming the service)
        max_concurrent = min(3, len(accounts))  # Max 3 concurrent requests
        semaphore = asyncio.Semaphore(max_concurrent)
        
        self.log(
            f"{Fore.GREEN + Style.BRIGHT}Processing {len(accounts)} accounts in parallel with {max_concurrent} concurrent workers{Style.RESET_ALL}"
        )
        
        # Create tasks for all accounts
        tasks = []
        for idx, account in enumerate(accounts, start=1):
            if account:
                task = asyncio.create_task(
                    self.process_single_account(account, use_proxy, idx, len(accounts), semaphore)
                )
                tasks.append(task)
                
                # Add longer delay between task creation for captcha stability
                if idx < len(accounts):
                    await asyncio.sleep(3)
        
        self.log(f"{Fore.BLUE + Style.BRIGHT}Waiting for all {len(tasks)} setup tasks to complete...{Style.RESET_ALL}")
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_count = 0
        failed_count = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.log(f"{Fore.RED + Style.BRIGHT}Task {i+1} failed with exception: {result}{Style.RESET_ALL}")
                failed_count += 1
            elif result:
                successful_count += 1
            else:
                failed_count += 1
        
        self.log(
            f"{Fore.GREEN + Style.BRIGHT}Parallel Setup Results: ✅ {successful_count} successful, ❌ {failed_count} failed{Style.RESET_ALL}"
        )
    
    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED + Style.BRIGHT}No Accounts Loaded.{Style.RESET_ALL}")
                return
            
            capctha_key = self.load_2captcha_key()
            if capctha_key:
                self.CAPTCHA_KEY = capctha_key
                self.log(f"{Fore.GREEN + Style.BRIGHT}🔐 2captcha API key loaded successfully{Style.RESET_ALL}")
            else:
                self.log(f"{Fore.RED + Style.BRIGHT}⚠️ WARNING: No 2captcha API key found!{Style.RESET_ALL}")
                self.log(f"{Fore.YELLOW + Style.BRIGHT}Please add your key to 2captcha_key.txt{Style.RESET_ALL}")
                return
            
            use_proxy_choice = self.print_question()
            processing_choice = self.print_processing_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            if processing_choice == 1:
                # ORIGINAL SEQUENTIAL METHOD - EXACTLY AS IT WAS
                separator = "="*25
                for idx, account in enumerate(accounts, start=1):
                    if account:
                        email = account["Email"]
                        password = account["Password"]
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}Of{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {len(accounts)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if not "@" in email or not password:
                            self.log(
                                f"{Fore.CYAN+Style.BRIGHT}Status :{Style.RESET_ALL}"
                                f"{Fore.RED+Style.BRIGHT} Invalid Account Data {Style.RESET_ALL}"
                            )
                            continue

                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}Account:{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(email)} {Style.RESET_ALL}"
                        )

                        self.password[email] = password

                        await self.process_accounts(email, use_proxy)
                        await asyncio.sleep(3)
            else:
                # PARALLEL METHOD
                separator = "="*75
                self.log(f"{Fore.CYAN + Style.BRIGHT}{separator}{Style.RESET_ALL}")
                await self.setup_tokens_parallel(accounts, use_proxy)
                self.log(f"{Fore.CYAN + Style.BRIGHT}{separator}{Style.RESET_ALL}")

            self.log(f"{Fore.CYAN + Style.BRIGHT}={'='*68}{Style.RESET_ALL}")

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

# Standalone function to run setup from bot.py
async def run_setup_for_failed_accounts(failed_accounts):
    """Run setup process for specific failed accounts using ORIGINAL method"""
    bot = DDAI()
    
    # Load captcha key
    captcha_key = bot.load_2captcha_key()
    if captcha_key:
        bot.CAPTCHA_KEY = captcha_key
    
    # Load proxies (use existing proxy.txt)
    try:
        if os.path.exists("proxy.txt"):
            with open("proxy.txt", 'r') as f:
                bot.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
    except:
        pass
    
    use_proxy = len(bot.proxies) > 0
    
    # Process failed accounts using ORIGINAL sequential method
    separator = "="*25
    for idx, account in enumerate(failed_accounts, start=1):
        if account:
            email = account["Email"]
            password = account["Password"]
            bot.log(
                f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT}Of{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {len(failed_accounts)} {Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
            )

            if not "@" in email or not password:
                bot.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Invalid Account Data {Style.RESET_ALL}"
                )
                continue

            bot.log(
                f"{Fore.CYAN + Style.BRIGHT}Account:{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {bot.mask_account(email)} {Style.RESET_ALL}"
            )

            bot.password[email] = password

            await bot.process_accounts(email, use_proxy)
            await asyncio.sleep(3)
    
    return True

if __name__ == "__main__":
    try:
        bot = DDAI()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(f"""
{Fore.YELLOW + Style.BRIGHT}╔════════════════════════════════════════════════════════════════════╗
║  {Fore.RED + Style.BRIGHT}🛑 SETUP CANCELLED 🛑{Fore.YELLOW + Style.BRIGHT}                                         ║
║                                                                    ║
║  {Fore.WHITE + Style.BRIGHT}👋 Setup interrupted by user{Fore.YELLOW + Style.BRIGHT}                                ║
║  {Fore.WHITE + Style.BRIGHT}💡 Run again when ready to continue{Fore.YELLOW + Style.BRIGHT}                        ║
║                                                                    ║
║  {Fore.CYAN + Style.BRIGHT}📧 Original by: vonssy | Enhanced by: jack0z{Fore.YELLOW + Style.BRIGHT}                ║
╚════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """)
    except Exception as e:
        print(f"""
{Fore.RED + Style.BRIGHT}╔════════════════════════════════════════════════════════════════════╗
║  {Fore.YELLOW + Style.BRIGHT}💥 SETUP ERROR 💥{Fore.RED + Style.BRIGHT}                                             ║
║                                                                    ║
║  {Fore.WHITE + Style.BRIGHT}❌ Setup failed: {str(e)[:45]}...{Fore.RED + Style.BRIGHT}                               ║
║  {Fore.WHITE + Style.BRIGHT}📞 Please check your configuration{Fore.RED + Style.BRIGHT}                            ║
║                                                                    ║
║  {Fore.CYAN + Style.BRIGHT}📧 Original by: vonssy | Enhanced by: jack0z{Fore.RED + Style.BRIGHT}                  ║
╚════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """)
        raise