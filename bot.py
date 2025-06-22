from curl_cffi import requests
from fake_useragent import FakeUserAgent
from datetime import datetime, timedelta
from colorama import *
import asyncio, base64, time, json, os, pytz, logging, schedule, random, traceback
import cloudscraper
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

wib = pytz.timezone('Asia/Jakarta')

# MongoDB connection
MONGODB_URI = os.environ.get("MONGODB_URI")

# Setup logging for point tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ddai_points_tracker.log', encoding='utf-8'),
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
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.access_tokens = {}
        self.refresh_tokens = {}
        
        # Point logging system
        self.db_client = None
        self.db = None
        self.collection = None
        self.setup_database()
        
        # Track last database update time per account (for hourly updates only)
        self.last_db_update = {}
        
        # Initialize cloudscraper session for point logging
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )

    def setup_database(self):
        """Initialize MongoDB connection for point tracking"""
        try:
            if MONGODB_URI:
                self.db_client = MongoClient(MONGODB_URI)
                self.db = self.db_client['ddai_farming']
                self.collection = self.db['ddai_points_tracker']
                
                # Drop existing indexes
                self.collection.drop_indexes()
                
                # Create indexes for better performance
                self.collection.create_index([("user_id", 1), ("timestamp", -1)])
                # Separate indexes for different document types
                self.collection.create_index([("type", 1), ("user_id", 1)], unique=True, 
                                           partialFilterExpression={"type": "summary"})
                self.collection.create_index([("type", 1), ("user_id", 1), ("date", 1)], unique=True,
                                           partialFilterExpression={"type": "daily_earning"})
                
                # Test connection
                self.db_client.admin.command('ping')
                logger.info("MongoDB connection established for point tracking")
            else:
                logger.warning("MONGODB_URI not found in environment variables. Point tracking disabled.")
                
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed: {e}")
            self.db_client = None
        except Exception as e:
            logger.warning(f"MongoDB setup warning: {e}")
            self.db_client = None

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
║  {Fore.YELLOW + Style.BRIGHT}🚀 DDAI NETWORK - ULTIMATE FARMING BOT 🚀{Fore.CYAN + Style.BRIGHT}                    ║
║                                                                  ║
║  {Fore.GREEN + Style.BRIGHT}💎 Enhanced Multi-Account Auto Farmer 💎{Fore.CYAN + Style.BRIGHT}                     ║
║                                                                  ║
║  {Fore.MAGENTA + Style.BRIGHT}⚡ Features:{Fore.CYAN + Style.BRIGHT}                                                ║
║    {Fore.WHITE + Style.BRIGHT}🔄 Auto Token Refresh & Re-authentication{Fore.CYAN + Style.BRIGHT}                  ║
║    {Fore.WHITE + Style.BRIGHT}🎯 Smart Mission Completion{Fore.CYAN + Style.BRIGHT}                               ║
║    {Fore.WHITE + Style.BRIGHT}📊 Real-time Points Tracking{Fore.CYAN + Style.BRIGHT}                              ║
║    {Fore.WHITE + Style.BRIGHT}🛡️ Advanced Error Recovery{Fore.CYAN + Style.BRIGHT}                                ║
║    {Fore.WHITE + Style.BRIGHT}🌐 Multi-Proxy Support{Fore.CYAN + Style.BRIGHT}                                    ║
║    {Fore.WHITE + Style.BRIGHT}💾 MongoDB Point Logging{Fore.CYAN + Style.BRIGHT}                                  ║
║                                                                  ║
║  {Fore.BLUE + Style.BRIGHT}👨‍💻 Original Creator: vonssy{Fore.CYAN + Style.BRIGHT}                                  ║
║  {Fore.BLUE + Style.BRIGHT}🔧 Enhanced by: jack0z{Fore.CYAN + Style.BRIGHT}                                       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.RED + Style.BRIGHT}⚠️  DISCLAIMER: Use at your own risk! {Fore.YELLOW + Style.BRIGHT}Educational purposes only! ⚠️{Style.RESET_ALL}
        """)

    def print_status_header(self):
        """Print a beautiful status header"""
        print(f"""
{Fore.CYAN + Style.BRIGHT}╔════════════════════════════════════════════════════════════════════╗
║  {Fore.YELLOW + Style.BRIGHT}🎮 BOT STATUS & CONFIGURATION 🎮{Fore.CYAN + Style.BRIGHT}                              ║
╚════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """)

    def print_accounts_loaded(self, count):
        """Print accounts loaded with emojis"""
        self.log(
            f"{Fore.GREEN + Style.BRIGHT}👥 Accounts Loaded: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{count}{Style.RESET_ALL} "
            f"{Fore.YELLOW + Style.BRIGHT}{'🔥' if count > 10 else '⭐'}{Style.RESET_ALL}"
        )

    def print_database_status(self):
        """Print database connection status"""
        if self.db_client:
            self.log(f"{Fore.GREEN + Style.BRIGHT}💾 Database: {Fore.WHITE + Style.BRIGHT}Connected ✅{Style.RESET_ALL}")
        else:
            self.log(f"{Fore.YELLOW + Style.BRIGHT}💾 Database: {Fore.WHITE + Style.BRIGHT}Disabled (Point logging off) ⚠️{Style.RESET_ALL}")

    def print_final_status(self):
        """Print final status when bot starts"""
        print(f"""
{Fore.GREEN + Style.BRIGHT}╔════════════════════════════════════════════════════════════════════╗
║  {Fore.YELLOW + Style.BRIGHT}🚀 BOT LAUNCHED SUCCESSFULLY! 🚀{Fore.GREEN + Style.BRIGHT}                             ║
║                                                                    ║
║  {Fore.WHITE + Style.BRIGHT}🤖 All accounts are now farming...{Fore.GREEN + Style.BRIGHT}                           ║
║  {Fore.WHITE + Style.BRIGHT}📈 Real-time stats updating every minute{Fore.GREEN + Style.BRIGHT}                     ║
║  {Fore.WHITE + Style.BRIGHT}💰 Points logged hourly to database{Fore.GREEN + Style.BRIGHT}                          ║
║  {Fore.WHITE + Style.BRIGHT}🔄 Auto-recovery enabled for all errors{Fore.GREEN + Style.BRIGHT}                      ║
║                                                                    ║
║  {Fore.CYAN + Style.BRIGHT}Press Ctrl+C to stop the bot{Fore.GREEN + Style.BRIGHT}                                 ║
╚════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """)

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "tokens.json"
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
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                with open(filename, 'r') as file:
                    existing_accounts = json.load(file)
            else:
                existing_accounts = []

            account_dict = {acc["Email"]: acc for acc in existing_accounts}

            for new_acc in new_accounts:
                account_dict[new_acc["Email"]] = new_acc

            updated_accounts = list(account_dict.values())

            with open(filename, 'w') as file:
                json.dump(updated_accounts, file, indent=4)

        except Exception as e:
            return []

    def load_credentials(self):
        filename = "accounts.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return []

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []

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
    
    def get_token_exp_time(self, token: str):
        try:
            header, payload, signature = token.split(".")
            decoded_payload = base64.urlsafe_b64decode(payload + "==").decode("utf-8")
            parsed_payload = json.loads(decoded_payload)
            exp_time = parsed_payload["exp"]
            
            return exp_time
        except Exception as e:
            return None

    def extract_user_id_from_token(self, token):
        """Extract user ID from JWT token for point tracking"""
        try:
            # JWT tokens are in format: header.payload.signature
            payload = token.split('.')[1]
            # Add padding if needed
            payload += '=' * (-len(payload) % 4)
            # Decode base64
            decoded = base64.b64decode(payload)
            token_data = json.loads(decoded)
            user_id = token_data.get('userId') or token_data.get('sub')  # Try both fields
            if not user_id:
                logger.error("No user ID found in JWT token")
                return None
            return user_id
        except Exception as e:
            logger.error(f"Error decoding JWT token: {e}")
            return None
            
    def biner_to_desimal(self, troughput: str):
        desimal = int(troughput, 2)
        return desimal

    def binary_to_decimal(self, throughput: str):
        """Convert binary throughput to decimal"""
        try:
            decimal = int(throughput, 2)
            return decimal
        except:
            return 0
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"
    
    def print_message(self, account, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(account)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        print(f"""
{Fore.CYAN + Style.BRIGHT}╔════════════════════════════════════════════════════════════════════╗
║  {Fore.YELLOW + Style.BRIGHT}🌐 PROXY CONFIGURATION 🌐{Fore.CYAN + Style.BRIGHT}                                     ║
╚════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """)
        
        while True:
            try:
                print(f"{Fore.GREEN + Style.BRIGHT}🔹 {Fore.WHITE + Style.BRIGHT}1. {Fore.CYAN + Style.BRIGHT}🆓 Free Proxyscrape Proxy {Fore.YELLOW + Style.BRIGHT}(Automatic Download){Style.RESET_ALL}")
                print(f"{Fore.GREEN + Style.BRIGHT}🔹 {Fore.WHITE + Style.BRIGHT}2. {Fore.CYAN + Style.BRIGHT}🔒 Private Proxy {Fore.YELLOW + Style.BRIGHT}(From proxy.txt){Style.RESET_ALL}")
                print(f"{Fore.GREEN + Style.BRIGHT}🔹 {Fore.WHITE + Style.BRIGHT}3. {Fore.CYAN + Style.BRIGHT}🚫 No Proxy {Fore.YELLOW + Style.BRIGHT}(Direct Connection){Style.RESET_ALL}")
                print()
                choose = int(input(f"{Fore.MAGENTA + Style.BRIGHT}🎯 Select option [1/2/3] ➤ {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "🆓 Free Proxyscrape" if choose == 1 else 
                        "🔒 Private Proxy" if choose == 2 else 
                        "🚫 No Proxy"
                    )
                    print(f"\n{Fore.GREEN + Style.BRIGHT}✅ {proxy_type} Selected!{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Invalid choice! Please enter 1, 2, or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}❌ Invalid input! Please enter a number (1, 2, or 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            print(f"""
{Fore.CYAN + Style.BRIGHT}╔════════════════════════════════════════════════════════════════════╗
║  {Fore.YELLOW + Style.BRIGHT}🔄 PROXY ROTATION SETTINGS 🔄{Fore.CYAN + Style.BRIGHT}                                 ║
╚════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
            """)
            while True:
                rotate = input(f"{Fore.MAGENTA + Style.BRIGHT}🔄 Enable proxy rotation on failures? {Fore.GREEN + Style.BRIGHT}[y/n] ➤ {Style.RESET_ALL}").strip().lower()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    status = f"🔄 {Fore.GREEN + Style.BRIGHT}Enabled" if rotate else f"🚫 {Fore.YELLOW + Style.BRIGHT}Disabled"
                    print(f"\n{Fore.CYAN + Style.BRIGHT}Proxy Rotation: {status}{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Invalid input! Enter 'y' for yes or 'n' for no.{Style.RESET_ALL}")

        return choose, rotate

    async def onchain_trigger(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/onchainTrigger"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": f"Bearer {self.access_tokens[user_id]}",
            "Content-Length":"0",
            "Origin": "chrome-extension://pigpomlidebemiifjihbgicepgbamdaj",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Storage-Access": "active",
            "User-Agent": FakeUserAgent().random
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)
                
                # Handle 401 errors with automatic re-setup
                if response.status_code == 401:
                    self.print_message(user_id, proxy, Fore.YELLOW, "Token expired, running automatic re-setup...")
                    setup_success = await self.run_setup_for_account(user_id)
                    if setup_success:
                        # Update headers with new token and retry
                        headers["Authorization"] = f"Bearer {self.access_tokens[user_id]}"
                        continue
                    else:
                        self.print_message(user_id, proxy, Fore.RED, "Auto re-setup failed")
                        return None
                
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(user_id, proxy, Fore.YELLOW, f"Onchain Trigger Failed: {Fore.RED+Style.BRIGHT}{str(e)}")

        return None

    async def run_setup_for_account(self, email):
        """Run setup process for a specific failed account"""
        try:
            # Import the setup function
            from setup import run_setup_for_failed_accounts
            
            # Load credentials for this specific account
            credentials = self.load_credentials()
            failed_account = None
            
            for cred in credentials:
                if cred.get("Email") == email:
                    failed_account = cred
                    break
            
            if not failed_account:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ No credentials found for {email} in accounts.json{Style.RESET_ALL}")
                return False
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔄 AUTOMATIC RE-SETUP STARTING for {self.mask_account(email)}{Style.RESET_ALL}")
            
            # Run setup for this specific account
            success = await run_setup_for_failed_accounts([failed_account])
            
            if success:
                # Reload tokens after successful setup
                tokens = self.load_accounts()
                for token in tokens:
                    if token.get("Email") == email:
                        self.access_tokens[email] = token["accessToken"]
                        self.refresh_tokens[email] = token["refreshToken"]
                        self.log(f"{Fore.GREEN + Style.BRIGHT}✅ Successfully re-setup tokens for {email}{Style.RESET_ALL}")
                        return True
            
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Failed to re-setup tokens for {email}{Style.RESET_ALL}")
            return False
            
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Failed to run setup for {email}: {e}{Style.RESET_ALL}")
            return False

    async def auth_refresh(self, email: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/refresh"
        data = json.dumps({"refreshToken":self.refresh_tokens[email]})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)
                if response.status_code == 401:
                    self.print_message(email, proxy, Fore.RED, "Refreshing Access Token Failed: "
                        f"{Fore.YELLOW + Style.BRIGHT}Token Expired, Running Auto Re-setup...{Style.RESET_ALL}"
                    )
                    
                    # Automatic re-setup on 401 error
                    setup_success = await self.run_setup_for_account(email)
                    if setup_success:
                        return "REAUTH_SUCCESS"  # Special return code to indicate re-auth was successful
                    else:
                        return None
                elif response.status_code == 403:
                    self.print_message(email, proxy, Fore.RED, "Refreshing Access Token Failed: "
                        f"{Fore.YELLOW + Style.BRIGHT}Invalid, Running Auto Re-setup...{Style.RESET_ALL}"
                    )
                    
                    # Automatic re-setup on 403 error
                    setup_success = await self.run_setup_for_account(email)
                    if setup_success:
                        return "REAUTH_SUCCESS"  # Special return code to indicate re-auth was successful
                    else:
                        return None
                    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, proxy, Fore.YELLOW, f"Refreshing Access Token Failed: {Fore.RED+Style.BRIGHT}{str(e)}")

        return None

    def save_to_database(self, trigger_data, throughput_data, account_name, user_id):
        """Save data to MongoDB using upsert operations (Nodepay pattern)"""
        try:
            if not self.db_client:
                return  # Skip if no database connection
                
            timestamp = datetime.now()
            
            if not trigger_data:
                logger.warning(f"No trigger data for user {user_id}")
                return
            
            # Extract relevant data from trigger_data
            requests_total = trigger_data.get('requestsTotal', 0)
            request_rate = trigger_data.get('requestRate', 0)
            request_24h = trigger_data.get('request24h', 0)
            join_date = trigger_data.get('joinDate', '')
            
            # Calculate throughput percentage
            throughput_percent = 0
            if throughput_data and throughput_data.get('throughput'):
                throughput_percent = self.binary_to_decimal(throughput_data['throughput'])
            
            # Update or insert daily record
            daily_doc = {
                'type': 'daily_earning',
                'user_id': user_id,
                'account_name': account_name,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'request_24h': request_24h,
                'timestamp': timestamp
            }
            
            try:
                self.collection.update_one(
                    {
                        'type': 'daily_earning',
                        'user_id': user_id,
                        'date': daily_doc['date']
                    },
                    {'$set': daily_doc},
                    upsert=True
                )
            except DuplicateKeyError:
                logger.warning(f"Duplicate daily record for user {user_id} on {daily_doc['date']}")
            
            # Update or insert summary record
            summary_doc = {
                'type': 'summary',
                'user_id': user_id,
                'account_name': account_name,
                'requests_total': requests_total,
                'request_rate': request_rate,
                'request_24h': request_24h,
                'throughput_percent': throughput_percent,
                'join_date': join_date,
                'last_updated': timestamp,
                'raw_data': {
                    'trigger_data': trigger_data,
                    'throughput_data': throughput_data
                }
            }
            
            try:
                self.collection.update_one(
                    {
                        'type': 'summary',
                        'user_id': user_id
                    },
                    {'$set': summary_doc},
                    upsert=True
                )
            except DuplicateKeyError:
                logger.warning(f"Duplicate summary record for user {user_id}")
            
            logger.info(f"Updated database for user {user_id}: {requests_total:,} total requests, {request_24h:,} 24h requests, {request_rate} rate, {throughput_percent}% throughput")
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            logger.error(traceback.format_exc())
            
    async def model_response(self, email: str, use_proxy: bool, rotate_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/modelResponse"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[email]}"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)
                
                # Handle 401 errors with automatic re-setup
                if response.status_code == 401:
                    self.print_message(email, proxy, Fore.YELLOW, "Token expired, running automatic re-setup...")
                    setup_success = await self.run_setup_for_account(email)
                    if setup_success:
                        # Update headers with new token and retry
                        headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
                        continue
                    else:
                        self.print_message(email, proxy, Fore.RED, "Auto re-setup failed")
                        return None
                
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, proxy, Fore.YELLOW, f"GET Troughput Data Failed: {Fore.RED+Style.BRIGHT}{str(e)}")

        return None
    
    async def mission_lists(self, email: str, use_proxy: bool, rotate_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/missions"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[email]}"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)
                
                # Handle 401 errors with automatic re-setup
                if response.status_code == 401:
                    self.print_message(email, proxy, Fore.YELLOW, "Token expired, running automatic re-setup...")
                    setup_success = await self.run_setup_for_account(email)
                    if setup_success:
                        # Update headers with new token and retry
                        headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
                        continue
                    else:
                        self.print_message(email, proxy, Fore.RED, "Auto re-setup failed")
                        return None
                
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, proxy, Fore.YELLOW, f"GET Mission Lists Failed: {Fore.RED+Style.BRIGHT}{str(e)}")

        return None
    
    async def complete_missions(self, email: str, mission_id: str, title: str, use_proxy: bool, rotate_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/missions/claim/{mission_id}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[email]}",
            "Content-Length":"0"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)
                
                # Handle 401 errors with automatic re-setup
                if response.status_code == 401:
                    self.print_message(email, proxy, Fore.YELLOW, "Token expired, running automatic re-setup...")
                    setup_success = await self.run_setup_for_account(email)
                    if setup_success:
                        # Update headers with new token and retry
                        headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
                        continue
                    else:
                        self.print_message(email, proxy, Fore.RED, "Auto re-setup failed")
                        return None
                
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, proxy, Fore.WHITE, f"Mission {title}"
                    f"{Fore.RED + Style.BRIGHT} Not Completed: {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None

    async def process_auth_refresh(self, email: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            refresh = await self.auth_refresh(email, proxy)
            if refresh == "REAUTH_SUCCESS":
                # Re-authentication was successful, tokens are already updated
                self.print_message(email, proxy, Fore.GREEN, "Re-authentication Success")
                return True
            elif refresh:
                self.access_tokens[email] = refresh["data"]["accessToken"]

                self.save_tokens([{"Email":email, "accessToken":self.access_tokens[email], "refreshToken":self.refresh_tokens[email]}])
                self.print_message(email, proxy, Fore.GREEN, "Refreshing Access Token Success")
                return True
            
            if rotate_proxy:
                proxy = self.rotate_proxy_for_account(email)

            await asyncio.sleep(5)
            continue
        
    async def check_token_exp_time(self, email: str, use_proxy: bool, rotate_proxy: bool):
        exp_time = self.get_token_exp_time(self.access_tokens[email])

        if int(time.time()) > exp_time:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            self.print_message(email, proxy, Fore.YELLOW, "Access Token Expired, Refreshing...")
            await self.process_auth_refresh(email, use_proxy, rotate_proxy)

        return True

    async def looping_auth_refresh(self, email: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            await asyncio.sleep(10 * 60)
            await self.process_auth_refresh(email, use_proxy, rotate_proxy)

    async def process_onchain_trigger(self, email: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.check_token_exp_time(email, use_proxy, rotate_proxy)
        if is_valid:
            while True:
                proxy = self.get_next_proxy_for_account(email) if use_proxy else None

                model = await self.onchain_trigger(email, proxy)
                if model:
                    req_total = model.get("data", {}).get("requestsTotal", 0)
                    self.print_message(email, proxy, Fore.GREEN, "Onchain Triggered Successfully "
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Total Requests: {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{req_total}{Style.RESET_ALL}"
                    )
                    return True
                
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(email)

                await asyncio.sleep(5)
                continue
        
    async def process_model_response(self, email: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            model = await self.model_response(email, use_proxy, rotate_proxy, proxy)
            if model:
                throughput = model.get("data", {}).get("throughput", 0)
                formatted_throughput = self.biner_to_desimal(throughput)

                self.print_message(email, proxy, Fore.GREEN, "Throughput "
                    f"{Fore.WHITE + Style.BRIGHT}{formatted_throughput}%{Style.RESET_ALL}"
                )

                # Point logging: Save to database only once per hour per account
                if self.db_client:
                    current_time = time.time()
                    last_update = self.last_db_update.get(email, 0)
                    
                    # Check if an hour (3600 seconds) has passed since last update
                    if current_time - last_update >= 3600:
                        user_id = self.extract_user_id_from_token(self.access_tokens[email])
                        if user_id:
                            # Get onchain trigger data for comprehensive logging
                            trigger_data = await self.onchain_trigger(email, proxy)
                            if trigger_data and trigger_data.get("data"):
                                self.save_to_database(
                                    trigger_data.get("data"), 
                                    model.get("data"), 
                                    email, 
                                    user_id
                                )
                                # Update the last database update timestamp
                                self.last_db_update[email] = current_time
                                self.log(f"{Fore.BLUE + Style.BRIGHT}📊 Database updated for {self.mask_account(email)} (next update in 1 hour){Style.RESET_ALL}")

            await asyncio.sleep(60)

    async def process_user_missions(self, email: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            mission_lists = await self.mission_lists(email, use_proxy, rotate_proxy, proxy)
            if mission_lists:
                missions = mission_lists.get("data", {}).get("missions", [])

                if missions:
                    completed = False

                    for mission in missions:
                        if mission:
                            mission_id = mission.get("_id")
                            title = mission.get("title")
                            reward = mission.get("rewards", {}).get("requests", 0)
                            type = mission.get("type")
                            status = mission.get("status")

                            if type == 3:
                                if status == "COMPLETED":
                                    claim = await self.complete_missions(email, mission_id, title, use_proxy, rotate_proxy, proxy)
                                    if claim and claim.get("data", {}).get("claimed"):
                                        self.print_message(email, proxy, Fore.WHITE, f"Mission {title}"
                                            f"{Fore.GREEN + Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                            f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT}{reward} Requests{Style.RESET_ALL}"
                                        )
                                
                            else:
                                if status == "PENDING":
                                    claim = await self.complete_missions(email, mission_id, title, use_proxy, rotate_proxy, proxy)
                                    if claim and claim.get("data", {}).get("claimed"):
                                        self.print_message(email, proxy, Fore.WHITE, f"Mission {title}"
                                            f"{Fore.GREEN + Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                            f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT}{reward} Requests{Style.RESET_ALL}"
                                        )
                        else:
                            completed = True

                    if completed:
                        self.print_message(email, proxy, Fore.GREEN, "All Available Mission Is Completed")

            await asyncio.sleep(24 * 60 * 60)

    def get_points_stats(self):
        """Get current statistics for all accounts with sexy emoji display"""
        try:
            if not self.db_client:
                self.log(f"{Fore.YELLOW + Style.BRIGHT}💾 Database not connected - Point stats unavailable ⚠️{Style.RESET_ALL}")
                return []
                
            stats = []
            cursor = self.collection.find(
                {'type': 'summary'},
                {'_id': 0}
            ).sort('last_updated', -1)
            
            total_requests = 0
            total_24h_requests = 0
            
            print(f"""
{Fore.MAGENTA + Style.BRIGHT}╔════════════════════════════════════════════════════════════════════╗
║  {Fore.YELLOW + Style.BRIGHT}📊 DDAI POINTS SUMMARY 📊{Fore.MAGENTA + Style.BRIGHT}                                   ║
╚════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
            """)
            
            account_count = 0
            for doc in cursor:
                account_count += 1
                requests_total = doc.get('requests_total', 0)
                request_24h = doc.get('request_24h', 0)
                request_rate = doc.get('request_rate', 0)
                throughput_percent = doc.get('throughput_percent', 0)
                join_date = doc.get('join_date', 'Unknown')
                
                total_requests += requests_total
                total_24h_requests += request_24h
                
                # Emoji based on performance
                performance_emoji = "🔥" if throughput_percent >= 90 else "⚡" if throughput_percent >= 70 else "💫" if throughput_percent >= 50 else "⏳"
                
                self.log(f"{Fore.CYAN + Style.BRIGHT}🔹 {performance_emoji} {doc['account_name']}:{Style.RESET_ALL}")
                self.log(f"   {Fore.GREEN + Style.BRIGHT}💰 Total Requests: {Fore.WHITE + Style.BRIGHT}{requests_total:,}{Style.RESET_ALL}")
                self.log(f"   {Fore.YELLOW + Style.BRIGHT}📈 24h Requests: {Fore.WHITE + Style.BRIGHT}{request_24h:,}{Style.RESET_ALL}")
                self.log(f"   {Fore.BLUE + Style.BRIGHT}⚡ Request Rate: {Fore.WHITE + Style.BRIGHT}{request_rate}{Style.RESET_ALL}")
                self.log(f"   {Fore.MAGENTA + Style.BRIGHT}🚀 Throughput: {Fore.WHITE + Style.BRIGHT}{throughput_percent}%{Style.RESET_ALL}")
                self.log(f"   {Fore.CYAN + Style.BRIGHT}📅 Join Date: {Fore.WHITE + Style.BRIGHT}{join_date}{Style.RESET_ALL}")
                self.log(f"   {Fore.GRAY + Style.BRIGHT}🕒 Updated: {doc['last_updated']}{Style.RESET_ALL}")
                self.log("")
                
                stats.append({
                    'user_id': doc['user_id'],
                    'account_name': doc['account_name'],
                    'requests_total': requests_total,
                    'request_24h': request_24h,
                    'request_rate': request_rate,
                    'throughput_percent': throughput_percent,
                    'join_date': join_date,
                    'last_updated': doc['last_updated']
                })
            
            if account_count > 0:
                print(f"""
{Fore.GREEN + Style.BRIGHT}╔════════════════════════════════════════════════════════════════════╗
║  {Fore.YELLOW + Style.BRIGHT}📊 SUMMARY STATISTICS 📊{Fore.GREEN + Style.BRIGHT}                                     ║
║                                                                    ║
║  {Fore.WHITE + Style.BRIGHT}💰 Total Requests: {total_requests:,}{Fore.GREEN + Style.BRIGHT}                                         ║
║  {Fore.WHITE + Style.BRIGHT}📈 24h Requests: {total_24h_requests:,}{Fore.GREEN + Style.BRIGHT}                                          ║
║  {Fore.WHITE + Style.BRIGHT}👥 Active Accounts: {account_count}{Fore.GREEN + Style.BRIGHT}                                           ║
║  {Fore.WHITE + Style.BRIGHT}⚡ Avg Requests/Account: {total_requests//account_count if account_count > 0 else 0:,}{Fore.GREEN + Style.BRIGHT}                              ║
╚════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
                """)
            else:
                self.log(f"{Fore.YELLOW + Style.BRIGHT}📊 No point data available yet - accounts still initializing...{Style.RESET_ALL}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting points stats: {e}")
            return []
        
    async def process_accounts(self, email: str, use_proxy: bool, rotate_proxy: bool):
        triggered = await self.process_onchain_trigger(email, use_proxy, rotate_proxy)
        if triggered:
            # Initial database update when bot starts (if database is available)
            if self.db_client:
                proxy = self.get_next_proxy_for_account(email) if use_proxy else None
                user_id = self.extract_user_id_from_token(self.access_tokens[email])
                if user_id:
                    # Get initial data for database
                    trigger_data = await self.onchain_trigger(email, proxy)
                    model_data = await self.model_response(email, use_proxy, rotate_proxy, proxy)
                    
                    if trigger_data and trigger_data.get("data"):
                        self.save_to_database(
                            trigger_data.get("data"), 
                            model_data.get("data") if model_data else None, 
                            email, 
                            user_id
                        )
                        # Set initial timestamp to allow hourly updates from now
                        self.last_db_update[email] = time.time()
                        self.log(f"{Fore.BLUE + Style.BRIGHT}📊 Initial database update for {self.mask_account(email)} completed{Style.RESET_ALL}")
            
            # Show initial point stats
            self.get_points_stats()
            
            tasks = [
                asyncio.create_task(self.looping_auth_refresh(email, use_proxy, rotate_proxy)),
                asyncio.create_task(self.process_model_response(email, use_proxy, rotate_proxy)),
                asyncio.create_task(self.process_user_missions(email, use_proxy, rotate_proxy))
            ]
            await asyncio.gather(*tasks)
    
    async def main(self):
        try:
            # Clear screen and show welcome
            self.clear_terminal()
            self.welcome()
            
            tokens = self.load_accounts()
            if not tokens:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ No Accounts Loaded! Please check tokens.json{Style.RESET_ALL}")
                return
            
            # Show configuration header
            self.print_status_header()
            
            # Display accounts loaded with emoji
            self.print_accounts_loaded(len(tokens))
            
            # Display database status
            self.print_database_status()
            
            # Proxy configuration
            use_proxy_choice, rotate_proxy = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            # Load proxies if needed
            if use_proxy:
                self.log(f"{Fore.CYAN + Style.BRIGHT}🌐 Loading proxies...{Style.RESET_ALL}")
                await self.load_proxies(use_proxy_choice)

            # Print final launch status
            self.print_final_status()

            self.log(f"{Fore.CYAN + Style.BRIGHT}{'='*75}{Style.RESET_ALL}")

            tasks = []
            for idx, token in enumerate(tokens, start=1):
                if token:
                    email = token["Email"]
                    access_token = token["accessToken"]
                    refresh_token = token["refreshToken"]

                    if not "@" in email or not access_token or not refresh_token:
                        self.log(
                            f"{Fore.RED + Style.BRIGHT}❌ Account {idx}: Invalid Data - Skipping{Style.RESET_ALL}"
                        )
                        continue

                    exp_time = self.get_token_exp_time(refresh_token)
                    if int(time.time()) > exp_time:
                        self.log(
                            f"{Fore.RED + Style.BRIGHT}❌ Account {idx} ({self.mask_account(email)}): Refresh Token Expired - Skipping{Style.RESET_ALL}"
                        )
                        continue

                    self.access_tokens[email] = access_token
                    self.refresh_tokens[email] = refresh_token

                    self.log(f"{Fore.GREEN + Style.BRIGHT}🚀 Launching account {idx}: {self.mask_account(email)}{Style.RESET_ALL}")
                    tasks.append(asyncio.create_task(self.process_accounts(email, use_proxy, rotate_proxy)))

            if not tasks:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ No valid accounts to process!{Style.RESET_ALL}")
                return

            self.log(f"{Fore.YELLOW + Style.BRIGHT}⚡ Processing {len(tasks)} accounts simultaneously...{Style.RESET_ALL}")
            await asyncio.gather(*tasks)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}💥 Critical Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = DDAI()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(f"""
{Fore.RED + Style.BRIGHT}╔════════════════════════════════════════════════════════════════════╗
║  {Fore.YELLOW + Style.BRIGHT}🛑 BOT SHUTDOWN INITIATED 🛑{Fore.RED + Style.BRIGHT}                                   ║
║                                                                    ║
║  {Fore.WHITE + Style.BRIGHT}👋 Thanks for using DDAI Ultimate Bot!{Fore.RED + Style.BRIGHT}                         ║
║  {Fore.WHITE + Style.BRIGHT}💾 All data has been saved safely{Fore.RED + Style.BRIGHT}                              ║
║  {Fore.WHITE + Style.BRIGHT}🚀 See you next time, farmer!{Fore.RED + Style.BRIGHT}                                  ║
║                                                                    ║
║  {Fore.CYAN + Style.BRIGHT}📧 Original by: vonssy | Enhanced by: jack0z{Fore.RED + Style.BRIGHT}                    ║
╚════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """)
    except Exception as e:
        print(f"""
{Fore.RED + Style.BRIGHT}╔════════════════════════════════════════════════════════════════════╗
║  {Fore.YELLOW + Style.BRIGHT}💥 CRITICAL ERROR 💥{Fore.RED + Style.BRIGHT}                                           ║
║                                                                    ║
║  {Fore.WHITE + Style.BRIGHT}❌ Bot crashed with error: {str(e)[:40]}...{Fore.RED + Style.BRIGHT}                      ║
║  {Fore.WHITE + Style.BRIGHT}📞 Please report this to the developers{Fore.RED + Style.BRIGHT}                        ║
║                                                                    ║
║  {Fore.CYAN + Style.BRIGHT}📧 Original by: vonssy | Enhanced by: jack0z{Fore.RED + Style.BRIGHT}                    ║
╚════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """)
        raise