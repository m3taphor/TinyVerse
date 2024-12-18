import asyncio
import base64
import json
import shutil
import os
import random
import re
import datetime
import brotli
import functools
import string

from typing import Callable
from multiprocessing.util import debug
from time import time
from urllib.parse import unquote, quote

import aiohttp
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import (
    Unauthorized, UserDeactivated, AuthKeyUnregistered, UserDeactivatedBan,
    AuthKeyDuplicated, SessionExpired, SessionRevoked, FloodWait
)
from pyrogram.raw import types
from pyrogram.raw import functions

from bot.config import settings

from bot.utils import logger
from bot.exceptions import TelegramInvalidSessionException, TelegramProxyError
from .headers import headers

from random import randint, choices

from bot.utils.functions import unix_convert, stars_count, getGiftCode, newGiftCode, errorGiftCode

from ..utils.firstrun import append_line_to_file

def error_handler(func: Callable):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            await asyncio.sleep(1)
    return wrapper

class Tapper:
    def __init__(self, tg_client: Client, first_run: bool):
        self.tg_client = tg_client
        self.first_run = first_run
        self.session_name = tg_client.name
        self.bot_peer = 'tverse'
        self.bot_chatid = 7631205793
        self.app_version = '0.7.25'
        self.theme_params = "{\"accent_text_color\":\"#6ab2f2\",\"bg_color\":\"#17212b\",\"bottom_bar_bg_color\":\"#17212b\",\"button_color\":\"#5288c1\",\"button_text_color\":\"#ffffff\",\"destructive_text_color\":\"#ec3942\",\"header_bg_color\":\"#17212b\",\"hint_color\":\"#708499\",\"link_color\":\"#6ab3f3\",\"secondary_bg_color\":\"#232e3c\",\"section_bg_color\":\"#17212b\",\"section_header_text_color\":\"#6ab3f3\",\"section_separator_color\":\"#111921\",\"subtitle_text_color\":\"#708499\",\"text_color\":\"#f5f5f5\"}"
        self.boost_translation = {
            1: "3h +20% Speed",
            2: "12h +50% Speed",
            3: "3h Auto-Collect",
            4: "12h Auto-Collect"
        }

    async def get_tg_web_data(self, proxy: str | None) -> str:
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            if not self.tg_client.is_connected:
                await self.tg_client.connect()

            while True:
                try:
                    peer = await self.tg_client.resolve_peer(self.bot_peer)
                    break
                except FloodWait as fl:
                    fls = fl.value

                    logger.warning(f"{self.session_name} | FloodWait {fl}")
                    logger.info(f"{self.session_name} | Sleep {fls}s")
                    await asyncio.sleep(fls + 3)
            ref_key = random.choice([settings.REF_KEY, "galaxy-0001a845e80004f232c60000a43a7f"]) if settings.SUPPORT_AUTHOR else settings.REF_KEY
            ref_id = ref_key.removeprefix("galaxy-")
            
            web_view = await self.tg_client.invoke(functions.messages.RequestWebView(
                peer=types.InputPeerUser(
                    user_id=peer.user_id, 
                    access_hash=peer.access_hash
                    ),
                bot=types.InputUser(
                    user_id=peer.user_id,
                    access_hash=peer.access_hash
                ),
                url='https://app.tonverse.app/',
                start_param=ref_key,
                theme_params=types.DataJSON(data=self.theme_params),
                platform='tdesktop'
            ))
            
            web_view: types.web_view_result_url.WebViewResultUrl = web_view

            auth_url = web_view.url
            tg_web_data = unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
            
            user_data = unquote(tg_web_data.split('&user=')[1])
            username = user_data.split('"username":"')[1].split('"')[0].lower() if '"username":"' in user_data else None
            
            me = await self.tg_client.get_me()
            self.tg_client_id = me.id
            
            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

            return ref_id, tg_web_data, username

        except (Unauthorized, UserDeactivated, AuthKeyUnregistered, UserDeactivatedBan, AuthKeyDuplicated,
                SessionExpired, SessionRevoked):
            raise TelegramInvalidSessionException(f"Telegram session is invalid. Client: {self.tg_client.name}")
        except AttributeError as e:
            raise TelegramProxyError(e)
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error during Authorization: {error}")
            await asyncio.sleep(delay=3)
            
        finally:
            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

    @error_handler
    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='http://ip-api.com/json', timeout=aiohttp.ClientTimeout(20))
            response.raise_for_status()

            response_json = await response.json()
            ip = response_json.get('query', 'N/A')
            country = response_json.get('country', 'N/A')

            logger.info(f"{self.session_name} | Proxy IP : {ip} | Proxy Country : {country}")
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

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
        
        full_url = url or f"https://api.tonverse.app{endpoint or ''}"
        
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

        retries = 0
        max_retries = settings.MAX_REQUEST_RETRY
        
        while retries < max_retries:
            try:
                response = await http_client.request(method, full_url, headers=request_headers, **kwargs)
                response.raise_for_status()
                
                if settings.SAVE_RESPONSE_DATA:
                    response_data = ""
                    response_data += f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Session: {self.session_name}\n\n"
                    response_data += f"Request URL: {full_url}\n"

                    if method == 'POST':
                        request_body = kwargs.get('json', None)
                        if request_body is not None:
                            response_data += f"Request Body (JSON): {json.dumps(request_body, indent=2)}\n\n"
                        else:
                            request_body = kwargs.get('data', None)
                            if request_body is not None:
                                response_data += f"Request Body (Data): {request_body}\n\n"

                    response_data += f"Response Code: {response.status}\n"
                    response_data += f"Response Headers: {dict(response.headers)}\n"
                    response_data += f"Response Body: {await response.text()}\n"
                    response_data += "-" * 50 + "\n"
                    
                    with open("saved_data.txt", "a", encoding='utf8') as file:
                        file.write(response_data)
                response_json = await response.json()
                if (response_json.get("error", {}).get("code"), response_json.get("error", {}).get("text")) == (10429, "Too many requests"):
                    retries += 1
                    logger.warning(f"{self.session_name} | Received <r>'Too many requests</r>, retrying {retries}/{max_retries}...")
                    await asyncio.sleep(2 ** retries)
                    continue
                else:
                    return response_json
            except aiohttp.ClientResponseError as error:
                
                if settings.SAVE_RESPONSE_DATA:
                    response_data = ""
                    response_data += f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Session: {self.session_name}\n\n"
                    response_data += f"Request URL: {full_url}\n"

                    if method == 'POST':
                        request_body = kwargs.get('json', None)
                        if request_body is not None:
                            response_data += f"Request Body (JSON): {json.dumps(request_body, indent=2)}\n\n"
                        else:
                            request_body = kwargs.get('data', None)
                            if request_body is not None:
                                response_data += f"Request Body (Data): {request_body}\n\n"

                    response_data += f"Response Code: {error.status}\n"
                    response_data += f"Response Headers: {dict(error.headers)}\n"
                    response_data += f"Response Message: {await error.message}\n"
                    response_data += "-" * 50 + "\n"
                    
                    with open("saved_data.txt", "a", encoding='utf8') as file:
                        file.write(response_data)
                        
                if error.status == 503 or error.status == 500:
                    retries += 1
                    logger.warning(f"{self.session_name} | Received <r>{error.status}</r>, retrying {retries}/{max_retries}...")
                    await asyncio.sleep(2 ** retries)
                    continue
                else:
                    logger.error(f"{self.session_name} | HTTP error: {error}")
                    raise
            except (aiohttp.ClientError, Exception) as error:
                logger.error(f"{self.session_name} | Unknown error when processing request: {error}")
                raise
        logger.error(f"{self.session_name} | Max retries reached for 'Server Un-Reachable' error.")
        raise aiohttp.ClientResponseError(
            request_info=None,
            history=None,
            status=503,
            message="Max retries reached for 503 errors."
        )
    
    @error_handler
    async def login(self, http_client: aiohttp.ClientSession, init_data):
        additional_headers = {'X-Application-Version': self.app_version}
        urlencoded_data = {
            "bot_id": self.bot_chatid,
            "data": init_data
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/auth/telegram", urlencoded_data=urlencoded_data, extra_headers=additional_headers)
        if response and response.get("response", {}).get("session"):
            return response
        return None

    @error_handler
    async def user_data(self, http_client: aiohttp.ClientSession, session_token, id="undefined"):
        additional_headers = {'X-Application-Version': self.app_version}
        urlencoded_data = {
            "session": session_token,
            "id": id
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/user/info", urlencoded_data=urlencoded_data, extra_headers=additional_headers)
        if response.get('response'):
            return response
        return None
    
    @error_handler
    async def get_galaxy(self, http_client: aiohttp.ClientSession, session_token, id="null", member_id="null"):
        additional_headers = {'X-Application-Version': self.app_version}
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
        additional_headers = {'X-Application-Version': self.app_version}
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
        additional_headers = {'X-Application-Version': self.app_version}
        urlencoded_data = {
            "session": session_token
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/galaxy/collect", urlencoded_data=urlencoded_data, extra_headers=additional_headers)
        if response.get('response'):
            return response
        return None
    
    @error_handler
    async def get_boost(self, http_client: aiohttp.ClientSession, session_token):
        additional_headers = {'X-Application-Version': self.app_version}
        urlencoded_data = {
            "session": session_token
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/user/boosts", urlencoded_data=urlencoded_data, extra_headers=additional_headers)
        if response.get('response'):
            return response
        return None
    
    @error_handler
    async def activate_boost(self, http_client: aiohttp.ClientSession, session_token, boost_id):
        additional_headers = {'X-Application-Version': self.app_version}
        urlencoded_data = {
            "session": session_token,
            "boost_id": boost_id
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/boost/activate", urlencoded_data=urlencoded_data, extra_headers=additional_headers)
        if response.get("response", {}).get("success") == 1:
            return response
        return None
    
    @error_handler
    async def create_stars(self, http_client: aiohttp.ClientSession, session_token, galaxy_id, stars):
        urlencoded_data = {
            "session": session_token,
            "galaxy_id": galaxy_id,
            "stars": stars
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/stars/create", urlencoded_data=urlencoded_data)
        if response.get("response", {}).get("success") == 1:
            return response
        return None
    
    @error_handler
    async def create_gift(self, http_client: aiohttp.ClientSession, session_token, stars):
        urlencoded_data = {
            "session": session_token,
            "stars": stars
        }
        response = await self.make_request(http_client, 'POST', endpoint="/gift/create", urlencoded_data=urlencoded_data)
        if response.get("response", {}).get("success") == 1:
            return response
        return None
    
    @error_handler
    async def get_gift(self, http_client: aiohttp.ClientSession, session_token, gift_id):
        urlencoded_data = {
            "session": session_token,
            "gift_id": gift_id
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/gift/get", urlencoded_data=urlencoded_data)
        if response.get("response", {}).get("available") == True:
            return response
        elif response.get("response", {}).get("available") == False:
            return 'used'
        elif response.get("error", {}).get("code") == 10010:
            return 'incorrect'
        else:
            return None
    
    @error_handler
    async def redeem_gift(self, http_client: aiohttp.ClientSession, session_token, gift_id):
        urlencoded_data = {
            "session": session_token,
            "gift_id": gift_id
        }
        
        response = await self.make_request(http_client, 'POST', endpoint="/gift/accept", urlencoded_data=urlencoded_data)
        if response.get("response", {}).get("success") == 1:
            return 'self'
        elif response.get("error", {}).get("code") == 10010:
            return response
        else:
            return None

    async def run(self, user_agent: str, proxy: str | None) -> None:
        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None
        headers["User-Agent"] = user_agent

        async with aiohttp.ClientSession(headers=headers, connector=proxy_conn, trust_env=True) as http_client:
            if proxy:
                await self.check_proxy(http_client=http_client, proxy=proxy)

            delay = randint(settings.START_DELAY[0], settings.START_DELAY[1])
            logger.info(f"{self.session_name} | Starting in {delay} seconds")
            await asyncio.sleep(delay=delay)
            
            while True:
                try:
                    if settings.NIGHT_MODE:
                        current_utc_time = datetime.datetime.utcnow().time()

                        start_time = datetime.time(settings.NIGHT_TIME[0], 0)
                        end_time = datetime.time(settings.NIGHT_TIME[1], 0)

                        next_checking_time = randint(settings.NIGHT_CHECKING[0], settings.NIGHT_CHECKING[1])

                        if start_time <= current_utc_time <= end_time:
                            logger.info(f"{self.session_name} | Night-Mode is on, The current UTC time is {current_utc_time.replace(microsecond=0)}, next check-in on {round(next_checking_time / 3600, 1)} hours.")
                            await asyncio.sleep(next_checking_time)
                            continue

                    sleep_time = randint(settings.SLEEP_TIME[0], settings.SLEEP_TIME[1])

                    try:
                        ref_id, init_data, username = await self.get_tg_web_data(proxy=proxy)
                    except TelegramProxyError:
                        return logger.error(f"<r>The selected proxy cannot be applied to the Telegram client.</r>")
                    except Exception as e:
                        return logger.error(f"Stop Tapper. Reason: {e}")
                    
                    logger.info(f"{self.session_name} | Trying to login")
                    
                    # Login
                    login_data = await self.login(http_client, init_data=init_data)
                    if not login_data:
                        logger.error(f"{self.session_name} | Login Failed")
                        logger.info(f"{self.session_name} | Sleep <y>{round(sleep_time / 60, 1)}</y> min")
                        await asyncio.sleep(delay=sleep_time)
                        continue
                    
                    session_token = login_data.get("response", {}).get("session")
                    
                    logger.success(f"{self.session_name} | <g>🪐 Login Successful</g>")
                    
                    # User-Data
                    user_data = await self.user_data(http_client, session_token=session_token)
                    if not user_data:
                        logger.error(f"{self.session_name} | Unknown error while collecting User Data!")
                        logger.info(f"{self.session_name} | Sleep <y>{round(sleep_time / 60, 1)}</y> min")
                        await asyncio.sleep(delay=sleep_time)
                        break
                    
                    create_unix = int(user_data['response'].get('created')) or 946684800
                    created_day = unix_convert(create_unix)
                    
                    total_galaxy = user_data['response'].get('galaxy') or 0
                    total_dust = user_data['response'].get('dust_max') or 0
                    current_dust = user_data['response'].get('dust') or 0
                    
                    logger.info(f"{self.session_name} | Galaxy: <y>{total_galaxy}</y> | Total Dust: <y>({current_dust}/{total_dust})</y> | Joined on: <y>{created_day}</y>")
                    await asyncio.sleep(random.randint(1, 3))
                    
                    # Create Galaxy
                    if total_galaxy <= 0:
                        logger.info(f"{self.session_name} | Creating Galaxy...")
                        create_galaxy = await self.begin_galaxy(http_client, session_token=session_token, stars=100, referral=ref_id)
                        if not create_galaxy:
                            logger.error(f"{self.session_name} | Unknown error while creating galaxy!")
                            logger.info(f"{self.session_name} | Sleep <y>{round(sleep_time / 60, 1)}</y> min")
                            await asyncio.sleep(delay=sleep_time)
                            break
                        logger.success(f"{self.session_name} | Galaxy has been successfully created.")
                        await asyncio.sleep(random.randint(1, 3))
                        
                    # Galaxy Info
                    galaxy_data = await self.get_galaxy(http_client, session_token=session_token)
                    if not galaxy_data:
                        logger.error(f"{self.session_name} | Unknown error while collecting Galaxy Data!")
                        logger.info(f"{self.session_name} | Sleep <y>{round(sleep_time / 60, 1)}</y> min")
                        await asyncio.sleep(delay=sleep_time)
                        break
                    
                    total_stars = galaxy_data['response'].get('stars') or 0
                    total_max_stars = galaxy_data['response'].get('stars_max') or 0
                    galaxy_name = galaxy_data['response'].get('title') or None
                    created_on = int(galaxy_data['response'].get('created')) or 946684800
                    galaxy_day = unix_convert(created_on)
                    galaxy_id = galaxy_data['response'].get('id') or None 
                    
                    
                    logger.info(f"{self.session_name} | Current Galaxy: <y>{galaxy_name}</y> | Stars: <y>({total_stars}/{total_max_stars})</y> | Created on: <y>{galaxy_day}</y>")
                    await asyncio.sleep(random.randint(1, 3))
                    
                    # Auto Redeem Gift
                    if settings.AUTO_REDEEM_CODE:
                        gift_code = getGiftCode(username.lower())
                        if gift_code:
                            logger.info(f"{self.session_name} | Total Gift-Codes for <y>@{username}</y>: <y>{len(gift_code)}</y>. Initiating redemption...")

                            successful_activations = 0

                            for code in gift_code:
                                code_info = await self.get_gift(http_client, session_token=session_token, gift_id=code)
                                if not code_info:
                                    logger.error(f"{self.session_name} | Unknown error while collecting Code Info!")
                                    logger.info(f"{self.session_name} | Sleep <y>{round(sleep_time / 60, 1)}</y> min")
                                    await asyncio.sleep(delay=sleep_time)
                                    continue
                                
                                if code_info == 'used' or code_info == 'incorrect':
                                    logger.error(f"{self.session_name} | Skipping Code: <y>{code}</y> is {code_info}. Check 'gift-codes.json' for more info.")
                                    errorGiftCode(code, code_info)
                                    continue
                                
                                code_value = int(code_info['response'].get('value')) or 0
                                code_sender = code_info['response'].get('sender') or None

                                redeem_data = await self.redeem_gift(http_client, session_token=session_token, gift_id=code)
                                if redeem_data == 'self':
                                    logger.error(f"{self.session_name} | Skipping Code: <y>{code}</y>, Code is incorrect or self-made. Check 'gift-codes.json' for more info.")
                                    errorGiftCode(code, 'incorrect')
                                    continue
                                if not redeem_data:
                                    logger.error(f"{self.session_name} | Unknown error while Code Redeem!")
                                    logger.info(f"{self.session_name} | Sleep <y>{round(sleep_time / 60, 1)}</y> min")
                                    await asyncio.sleep(delay=sleep_time)
                                    continue
                                
                                successful_activations += 1
                                logger.success(f"{self.session_name} | Code Applied: <g>{code}</g> | Stars: <g>+{code_value}</g> | Sender: <y>@{code_sender}</y>")
                                errorGiftCode(code, 'used')

                                if successful_activations % 5 == 0:
                                    logger.info(f"{self.session_name} | Made {successful_activations} Successful 5 activations. Taking a break...")
                                    await asyncio.sleep(random.randint(10, 15))
                                else:
                                    await asyncio.sleep(random.randint(3, 5))

                            logger.info(f"{self.session_name} | All Gift-Codes processed!")
                            await asyncio.sleep(random.randint(1, 3))
                    
                    # Collect Dust
                    if settings.AUTO_COLLECT_DUST:
                        user_data = await self.user_data(http_client, session_token=session_token)
                        if not user_data:
                            logger.error(f"{self.session_name} | Unknown error while collecting User Data!")
                            logger.info(f"{self.session_name} | Sleep <y>{round(sleep_time / 60, 1)}</y> min")
                            await asyncio.sleep(delay=sleep_time)
                            break

                        dust_progress = float(user_data['response'].get('dust_progress')) or 0
                        if dust_progress > 0:
                            logger.info(f"{self.session_name} | Collecting Dust...")
                            collect_dust = await self.collect_dust(http_client, session_token=session_token)
                            if not collect_dust:
                                logger.error(f"{self.session_name} | Unknown error while collecting Dust!")
                                logger.info(f"{self.session_name} | Sleep <y>{round(sleep_time / 60, 1)}</y> min")
                                await asyncio.sleep(delay=sleep_time)
                                break
                            dust_collected = collect_dust['response'].get('dust') or 0
                            logger.success(f"{self.session_name} | Dust collected: <g>+{dust_collected}</g>")
                            
                        await asyncio.sleep(random.randint(1, 3))
                    
                    # Auto Create Stars
                    if settings.AUTO_CREATE_STAR:
                        star_allowed_username = [item.replace('@', '').lower() for item in settings.MAKE_STARS_ALLOWED_USERNAME]
                        star_restrict_username = [item.replace('@', '').lower() for item in settings.MAKE_STARS_RESTRICT_USERNAME]
                        
                        if (username in star_allowed_username or 'all' in star_allowed_username) and username not in star_restrict_username:
                            user_data = await self.user_data(http_client, session_token=session_token)
                            if not user_data:
                                logger.error(f"{self.session_name} | Unknown error while collecting User Data!")
                                logger.info(f"{self.session_name} | Sleep <y>{round(sleep_time / 60, 1)}</y> min")
                                await asyncio.sleep(delay=sleep_time)
                                break
                            
                            current_dust = int(user_data['response'].get('dust')) or 0
                            total_dust = int(user_data['response'].get('dust_max')) or 0
                            
                            current_stars = int(user_data['response'].get('stars')) or 0
                            total_stars = int(user_data['response'].get('stars_max')) or 0

                            stars_value = stars_count(current_dust, current_stars)
                            if stars_value > 100:
                                if settings.USE_DUST_PERCENTAGE == 0:
                                    dust_available = current_dust * 0.99
                                else:
                                    dust_available = (settings.USE_DUST_PERCENTAGE / 100) * total_dust * 0.99

                                calculated_stars = stars_count(dust_available, current_stars)

                                if calculated_stars > 100:
                                    logger.info(f"{self.session_name} | Creating Stars...")
                                    if galaxy_id:
                                        stars_data = await self.create_stars(http_client, session_token=session_token, galaxy_id=galaxy_id, stars=calculated_stars)
                                        if stars_data:
                                            logger.success(f"{self.session_name} | Stars Created: <g>+{calculated_stars}</g>")
                                            logger.info(f"{self.session_name} | Updated Dust: <y>({int(current_dust - dust_available)}/{total_dust})</y> | Updated Stars: <y>({current_stars + calculated_stars}/{total_stars})</y>")
                                    else:
                                        logger.error(f"{self.session_name} | Unable to find Galaxy-ID, Can not create Stars!")

                        await asyncio.sleep(random.randint(1, 3))
                    
                    # Auto Gift Stars
                    if settings.AUTO_GIFT_STAR:
                        gift_allowed_username = [item.replace('@', '').lower() for item in settings.MAKE_GIFT_ALLOWED_USERNAME]
                        gift_restrict_username = [item.replace('@', '').lower() for item in settings.MAKE_GIFT_RESTRICT_USERNAME]
                        gift_to_username = [item.replace('@', '').lower() for item in settings.GIFT_TO_USERNAME]
                        
                        if (username in gift_allowed_username or 'all' in settings.MAKE_GIFT_ALLOWED_USERNAME) and username not in gift_restrict_username and username not in gift_to_username:
                            user_data = await self.user_data(http_client, session_token=session_token)
                            if not user_data:
                                logger.error(f"{self.session_name} | Unknown error while collecting User Data!")
                                logger.info(f"{self.session_name} | Sleep <y>{round(sleep_time / 60, 1)}</y> min")
                                await asyncio.sleep(delay=sleep_time)
                                break
                            
                            current_dust = int(user_data['response'].get('dust')) or 0
                            total_dust = int(user_data['response'].get('dust_max')) or 0
                            current_stars = int(user_data['response'].get('stars')) or 0
                            stars_value = stars_count(current_dust, current_stars)
                            
                            if stars_value > 100:
                                if settings.GIFT_STAR_PERCENTAGE == 0:
                                    dust_available = current_dust * 0.99
                                else:
                                    dust_available = (settings.GIFT_STAR_PERCENTAGE / 100) * total_dust * 0.99

                                calculated_stars = stars_count(dust_available, current_stars)
                                
                                if calculated_stars > 100:
                                    logger.info(f"{self.session_name} | Creating {calculated_stars} Stars Gift-Code...")
                                    gift_data = await self.create_gift(http_client, session_token=session_token, stars=calculated_stars)
                                    if gift_data:
                                        gift_code = gift_data['response'].get('code')
                                        for_username = random.choice(settings.GIFT_TO_USERNAME)
                                        save_gift = newGiftCode(gift_code, for_username, calculated_stars)
                                        if save_gift == True: 
                                            logger.success(f"{self.session_name} | Gift-Code Created: <g>{gift_code}</g> for <y>@{for_username}</y>. You can edit JSON file and change Username.")
                                            logger.info(f"{self.session_name} | Saved Gift-Code in 'gift-codes.json', Using in next login. You can change username in json file.")
                                            logger.info(f"{self.session_name} | Updated Dust: <y>({int(current_dust - dust_available)}/{total_dust})</y>")
                                        else:
                                            logger.error(f"{self.session_name} | Error saving code: <y>{gift_code}</y> | Amount: <y>{calculated_stars} Stars</y> | Created By: <y>{username}</y>")
                    
                    # Apply Boost
                    if settings.AUTO_APPLY_BOOST:
                        boost_data = await self.get_boost(http_client, session_token=session_token)
                        if not boost_data:
                            logger.error(f"{self.session_name} | Unknown error while collecting Boost Data!")
                            logger.info(f"{self.session_name} | Sleep <y>{round(sleep_time / 60, 1)}</y> min")
                            await asyncio.sleep(delay=sleep_time)
                            break
                        
                        total_boost = int(boost_data['response'].get('count')) or 0
                        current_time = int(time())
                        boost_delay = 0
                        
                        if total_boost > 0:
                            for item in boost_data['response']['items']:
                                expires = int(item['expires']) or 0
                                boost_id = 0
                                count = int(item['count']) or 0
                                
                                if expires == 0 or current_time > expires and count > 0:
                                    boost_id = int(item['boost_id'])
                                    apply_boost = await self.activate_boost(http_client, session_token=session_token, boost_id=boost_id)
                                    if not apply_boost:
                                        logger.error(f"{self.session_name} | Unknown error while activating Boost!")
                                        logger.info(f"{self.session_name} | Sleep <y>{round(sleep_time / 60, 1)}</y> min")
                                        await asyncio.sleep(delay=sleep_time)
                                        break
                                    
                                    logger.success(f"{self.session_name} | Boost Activated <y>{boost_id}</y>: <g>({self.boost_translation.get(boost_id, 'N/A')})</g>")
                                
                                if boost_id == 4:  # 12 Hours boost
                                    boost_delay = max(boost_delay, 12 * 60 * 60)
                                elif boost_id == 3:  # 3 Hours boost
                                    boost_delay = max(boost_delay, 3 * 60 * 60)
                                
                                await asyncio.sleep(random.randint(1, 3))
                        if boost_delay > 0:
                            adjusted_sleep = boost_delay + random.randint(settings.EXTRA_BOOST_DELAY[0], settings.EXTRA_BOOST_DELAY[1]) - sleep_time
                            if adjusted_sleep > 0:
                                hours, minutes = divmod(adjusted_sleep // 60, 60)
                                logger.info(f"{self.session_name} | Sleep <y>{hours} hour, {minutes} mins</y>; due to auto-collect boost.")
                                await asyncio.sleep(adjusted_sleep)
                                
                                
                    logger.info(f"{self.session_name} | Sleep <y>{round(sleep_time / 60, 1)}</y> min")
                    await asyncio.sleep(delay=sleep_time)

                except Exception as error:
                    logger.error(f"{self.session_name} | Unknown error: {error}")
                    await asyncio.sleep(delay=3)

async def run_tapper(tg_client: Client, user_agent: str, proxy: str | None, first_run: bool):
    try:
        await Tapper(tg_client=tg_client, first_run=first_run).run(user_agent=user_agent, proxy=proxy)
    except TelegramInvalidSessionException:
        session_file = f"sessions/{tg_client.name}.session"
        if not os.path.exists("sessions/deleted_sessions"):
            os.makedirs("sessions/deleted_sessions", exist_ok=True)
        shutil.move(session_file, f"sessions/deleted_sessions/{tg_client.name}.session")
        logger.error(f"Telegram account {tg_client.name} is not work!")
