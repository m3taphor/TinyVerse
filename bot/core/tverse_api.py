import asyncio
from typing import Callable
import functools
import json

import aiohttp
import random
import string

from bot.config import settings
from bot.utils import logger
from bot.utils.functions import unix_time

API_URL = "https://api.tonverse.app"

def error_handler(func: Callable):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        retries = settings.MAX_RETRY_REQUEST
        for attempt in range(retries):
            try:
                response = await func(*args, **kwargs)
                if response and response.get("error", {}).get("text") == "Too many requests":
                    logger.warning(f"error | Received <r>'Too many requests</r>, {attempt + 1}/{retries}...")
                    await asyncio.sleep(2 ** retries)
                    continue
                else:
                    return response
            except Exception as e:
                with open("unknown_errors.txt", "a") as f:
                    f.write(f"Error in {func.__name__}: {e}\n")
                await asyncio.sleep(1)
                return
        logger.error(f"error | Failed to get request, Max tries reached: {retries}.")
        return None
    return wrapper

class TverseAPI:
    def __init__(self, app_version: str):
        self.app_version = app_version

    @error_handler
    async def make_request(
        self,
        http_client: aiohttp.ClientSession,
        method,
        endpoint=None,
        url=None,
        extra_headers=None,
        web_boundary=None,
        json_data=None,
        urlencoded_data=None,
        **kwargs
    ):
        full_url = url or API_URL + endpoint or ''
        
        request_headers = http_client._default_headers.copy()
        if extra_headers:
            request_headers.update(extra_headers)
            
        if web_boundary:
            boundary = "------WebKitFormBoundary" + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            body = "\r\n".join(
                f"{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{value}"
                for key, value in web_boundary.items()
            ) + f"\r\n{boundary}--\r\n"
            request_headers["Content-Type"] = f"multipart/form-data; boundary=----{boundary.strip('--')}"
            kwargs["data"] = body
            
        elif json_data is not None:
            request_headers["Content-Type"] = "application/json"
            kwargs["json"] = json_data
        elif urlencoded_data is not None:
            request_headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
            kwargs["data"] = aiohttp.FormData(urlencoded_data)

        response = await http_client.request(method, full_url, headers=request_headers, **kwargs)
        response.raise_for_status()

        return await response.json()

    @error_handler
    async def login(self, http_client: aiohttp.ClientSession, init_data):
        additional_headers = {'X-Application-Version': self.app_version, 'X-Client-Time-Diff': unix_time()}
        urlencoded_data = {
            "bot_id": 7631205793,
            "data": init_data
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/auth/telegram", urlencoded_data=urlencoded_data, extra_headers=additional_headers)
        if response and response.get("response", {}).get("session"):
            return response
        return None

    @error_handler
    async def user_data(self, http_client: aiohttp.ClientSession, session_token, id="undefined"):
        additional_headers = {'X-Application-Version': self.app_version, 'X-Client-Time-Diff': unix_time()}

        urlencoded_data = {
            "session": session_token,
            "id": id
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/user/info", urlencoded_data=urlencoded_data, extra_headers=additional_headers)
        if response and response.get('error'):
            return response
        if response and response.get('response'):
            return response
        return None

    @error_handler
    async def get_galaxy(self, http_client: aiohttp.ClientSession, session_token, id="null", member_id="null"):
        additional_headers = {'X-Application-Version': self.app_version, 'X-Client-Time-Diff': unix_time()}
        urlencoded_data = {
            "session": session_token,
            "id": id,
            "member_id": member_id
        }
        response = await self.make_request(http_client, 'POST', endpoint="/galaxy/get", urlencoded_data=urlencoded_data, extra_headers=additional_headers)
        if response.get('response'):
            return response
        return None

    @error_handler
    async def begin_galaxy(self, http_client: aiohttp.ClientSession, session_token, stars, referral):
        additional_headers = {'X-Application-Version': self.app_version, 'X-Client-Time-Diff': unix_time()}
        urlencoded_data = {
            "session": session_token,
            "stars": stars,
            "referral": referral
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/galaxy/begin", urlencoded_data=urlencoded_data, extra_headers=additional_headers)
        if response.get("response", {}).get("success") == 1:
            return response
        return None

    @error_handler
    async def collect_dust(self, http_client: aiohttp.ClientSession, session_token):
        additional_headers = {'X-Application-Version': self.app_version, 'X-Client-Time-Diff': unix_time()}
        urlencoded_data = {
            "session": session_token
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/galaxy/collect", urlencoded_data=urlencoded_data, extra_headers=additional_headers)
        if response.get('response'):
            return response
        return None

    @error_handler
    async def get_boost(self, http_client: aiohttp.ClientSession, session_token):
        additional_headers = {'X-Application-Version': self.app_version, 'X-Client-Time-Diff': unix_time()}
        urlencoded_data = {
            "session": session_token
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/user/boosts", urlencoded_data=urlencoded_data, extra_headers=additional_headers)
        if response.get('response'):
            return response
        return None

    @error_handler
    async def activate_boost(self, http_client: aiohttp.ClientSession, session_token, boost_id, boost_count):
        additional_headers = {'X-Application-Version': self.app_version, 'X-Client-Time-Diff': unix_time()}
        urlencoded_data = {
            "session": session_token,
            "boost_id": boost_id,
            "count": boost_count
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/boost/activate", urlencoded_data=urlencoded_data, extra_headers=additional_headers)
        if response.get("response", {}).get("success") == 1:
            return response
        return None

    @error_handler
    async def create_stars(self, http_client: aiohttp.ClientSession, session_token, galaxy_id, stars):
        additional_headers = {'X-Application-Version': self.app_version, 'X-Client-Time-Diff': unix_time()}
        urlencoded_data = {
            "session": session_token,
            "galaxy_id": galaxy_id,
            "stars": stars
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/stars/create", urlencoded_data=urlencoded_data, extra_headers=additional_headers)
        if response.get("response", {}).get("success") == 1:
            return response
        return None

    @error_handler
    async def get_gift(self, http_client: aiohttp.ClientSession, session_token, gift_id):
        additional_headers = {'X-Application-Version': self.app_version, 'X-Client-Time-Diff': unix_time()}
        urlencoded_data = {
            "session": session_token,
            "gift_id": gift_id
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/gift/get", urlencoded_data=urlencoded_data, extra_headers=additional_headers)
        if response.get("response", {}).get("available") == True:
            return response
        elif response.get("response", {}).get("available") == False:
            return response
        elif response.get("error", {}).get("code") == 10010:
            return response
        else:
            return None

    @error_handler
    async def redeem_gift(self, http_client: aiohttp.ClientSession, session_token, gift_id):
        additional_headers = {'X-Application-Version': self.app_version, 'X-Client-Time-Diff': unix_time()}
        urlencoded_data = {
            "session": session_token,
            "gift_id": gift_id
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/gift/accept", urlencoded_data=urlencoded_data, extra_headers=additional_headers)
        if response.get("response", {}).get("success") == 1:
            return response
        elif response.get("error", {}).get("code") == 10010:
            return response
        else:
            return None

    @error_handler
    async def get_civilization(self, http_client: aiohttp.ClientSession, session_token, galaxy_id):
        additional_headers = {'X-Application-Version': self.app_version, 'X-Client-Time-Diff': unix_time()}
        urlencoded_data = {
            "session": session_token,
            "civilization_id": None,
            "galaxy_id": galaxy_id
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/civilization/get", urlencoded_data=urlencoded_data, extra_headers=additional_headers)
        if response.get("response", {}):
            return response
        else:
            return None

    
    @error_handler
    async def scan_status(self, http_client: aiohttp.ClientSession, session_token):
        additional_headers = {'X-Application-Version': self.app_version, 'X-Client-Time-Diff': unix_time()}
        urlencoded_data = {
            "session": session_token
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/scan/status", urlencoded_data=urlencoded_data, extra_headers=additional_headers)
        if response.get("response", {}).get("status") == True:
            return response
        else:
            return None
        
    @error_handler
    async def scan_start(self, http_client: aiohttp.ClientSession, session_token, galaxy_id, power):
        additional_headers = {'X-Application-Version': self.app_version, 'X-Client-Time-Diff': unix_time()}
        urlencoded_data = {
            "session": session_token,
            "galaxy_id": galaxy_id,
            "power": power
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/scan/start", urlencoded_data=urlencoded_data, extra_headers=additional_headers)
        if response.get("response", {}).get("success") == 1:
            return response
        else:
            return None
        
    @error_handler
    async def scan_result(self, http_client: aiohttp.ClientSession, session_token, galaxy_id):
        additional_headers = {'X-Application-Version': self.app_version, 'X-Client-Time-Diff': unix_time()}
        urlencoded_data = {
            "session": session_token,
            "galaxy_id": galaxy_id
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/scan/result", urlencoded_data=urlencoded_data, extra_headers=additional_headers)
        if response.get("response", {}):
            return response
        else:
            return None
