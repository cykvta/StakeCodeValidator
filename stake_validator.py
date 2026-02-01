import requests
import logging
from datetime import datetime
import cloudscraper

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs.txt', encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)


class StakeValidator:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://stake.com/_api/graphql"
        self.headers = {
            "Content-Type": "application/json",
            "Cookie": f"session={token}",
            "x-access-token": token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Origin": "https://stake.com",
            "Referer": "https://stake.com/settings/general",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin"
        }
        self.username = None
        
        # Create session with cloudscraper
        self.session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
                }
            )
        
        logger.info("Using cloudscraper for Cloudflare bypass")
    
    def _make_request(self, payload: dict) -> dict:
        """Makes a POST request to Stake API"""
        try:
            response = self.session.post(
                self.base_url, 
                headers=self.headers, 
                json=payload,
                timeout=30
            )
            # Response log for debugging
            if response.status_code != 200:
                logger.error(f"Status: {response.status_code}, Response: {response.text[:500]}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return {"error": str(e)}

    def get_user_info(self) -> dict:
        """Gets basic user information"""
        query = """
        query UserInfo {
            user {
                id
                name
                email
                createdAt
                isKycBasicRequired
                isKycExtendedRequired
                isKycFullRequired
                kycStatus
                hasEmailVerified
                hasPhoneNumberVerified
                hasTfaEnabled
            }
        }
        """
        
        payload = {"query": query}
        return self._make_request(payload)

    def get_welcome_offer_code(self) -> dict:
        """Gets user welcome offer code"""
        # Query to get the signup/referral code
        query = """
        query GetUserAffiliateInfo {
            user {
                id
                name
                affiliateDealType
                signupCode {
                    code {
                        code
                        id
                    }
                }
            }
        }
        """
        
        payload = {"query": query}
        return self._make_request(payload)

    def get_wallets(self) -> dict:
        """Gets all user wallets"""
        # Main currencies list
        currencies = ["btc", "eth", "ltc", "doge", "bch", "xrp", "trx", "eos", "bnb", "usdt", "usdc", "busd", "sol", "pol", "link", "uni", "shib", "ape"]
        
        wallets = []
        for currency in currencies:
            query = f"""
            query GetDepositAddress {{
                user {{
                    id
                    depositAddress(currency: {currency}, type: default) {{
                        address
                        currency
                    }}
                }}
            }}
            """
            payload = {"query": query}
            result = self._make_request(payload)
            if "error" not in result:
                user_data = result.get("data", {}).get("user", {})
                if user_data:
                    deposit_info = user_data.get("depositAddress", {})
                    if deposit_info and deposit_info.get("address"):
                        wallets.append({
                            "currency": currency.upper(),
                            "address": deposit_info.get("address")
                        })
        
        return {"wallets": wallets}

    def validate_token(self) -> bool:
        """Validates if the token is valid"""
        result = self.get_user_info()
        if "error" in result:
            logger.error(f"Invalid token - Response error: {result.get('error')}")
            return False
        user_data = result.get("data", {}).get("user")
        if user_data is None:
            logger.error("Invalid token - User not found in response")
            return False
        self.username = user_data.get("name", None)
        return True

    def get_all_data(self) -> dict:
        """Gets all user data"""
        logger.info("Starting Stake.com account validation")
        
        response = {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "username": None,
            "data": None,
            "error": None
        }
        
        # Validate token
        if not self.validate_token():
            response["error"] = "Invalid or expired token"
            logger.error("Validation failed: Invalid or expired token")
            return response
        
        response["username"] = self.username
        logger.info(f"Token validated successfully - User: {self.username}")
        
        results = {}
        
        # 1. Get welcome offer code
        welcome_data = self.get_welcome_offer_code()
        if "error" not in welcome_data:
            user_data = welcome_data.get("data", {}).get("user", {})
            affiliate_deal_type = user_data.get("affiliateDealType", None)
            
            # Get signup code (streamer code like DRAKE, TRAINWRECK, etc.)
            signup_code_data = user_data.get("signupCode", {})
            signup_code = None
            if signup_code_data:
                code_obj = signup_code_data.get("code", {})
                if code_obj:
                    signup_code = code_obj.get("code", None)
            
            results["welcome_offer"] = {
                "signup_code": signup_code,
                "affiliate_deal_type": affiliate_deal_type
            }
            logger.info(f"Welcome offer code obtained: {signup_code}")
        else:
            results["welcome_offer"] = {"error": welcome_data.get("error")}
            logger.error(f"Error getting welcome offer code: {welcome_data.get('error')}")
        
        # 2. Get all wallets
        wallet_data = self.get_wallets()
        wallets_list = wallet_data.get("wallets", [])
        results["wallets"] = wallets_list
        logger.info(f"Wallets obtained: {len(wallets_list)}")
        
        response["success"] = True
        response["data"] = results
        
        logger.info("Query completed successfully")
        
        return response
