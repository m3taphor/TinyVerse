import os
import ssl
import math
import random
import shutil
import aiohttp
import asyncio
import datetime

from urllib.parse import unquote
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from random import randint
from time import time

from bot.utils.auth_token import append_token, get_token
from bot.utils.functions import calc_scan_chance, unix_convert, getGiftCode, errorGiftCode, stars_count, boostCount
from bot.utils.universal_telegram_client import UniversalTelegramClient

from .headers import *
from .tverse_api import TverseAPI

from bot.config import settings
from bot.utils import logger, log_error, config_utils, CONFIG_PATH, SESSIONS_PATH
from bot.exceptions import AuthError, InvalidSession

class Tapper:
    def __init__(self, tg_client: UniversalTelegramClient, app_id: str):
        self.tg_client = tg_client
        self.session_name = tg_client.session_name
        self.app_version = app_id
        self.auth_token = None
        self.boost_translation = {
            1: "+20% Speed",
            2: "+50% Speed",
            3: "Auto Collect",
        }

        session_config = config_utils.get_session_config(self.session_name, CONFIG_PATH)

        if not all(key in session_config for key in ('api', 'user_agent')):
            logger.critical(f"{self.session_name} | `accounts_config.json` might be corrupted or invalid.")
            exit(-1)

        self.headers = headers
        user_agent = session_config.get('user_agent')
        self.headers['User-Agent'] = user_agent
        self.headers.update(**get_sec_ch_ua(user_agent))

        self.proxy = session_config.get('proxy')
        if self.proxy:
            proxy = Proxy.from_str(self.proxy)
            self.tg_client.set_proxy(proxy)

    async def get_tg_web_data(self) -> str:
        webview_url = await self.tg_client.get_webview_url('tverse', "https://app.tonverse.app/", "galaxy-0003f55f8700024ba9d90003b65e7a")
        tg_web_data = unquote(string=webview_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])

        user_data = unquote(tg_web_data.split('&user=')[1])
        username = user_data.split('"username":"')[1].split('"')[0].lower() if '"username":"' in user_data else 'null'
        ref_id = user_data.split('"start_param":"')[1].split('"')[0].lower() if '"start_param":"' in user_data else 'galaxy-0003f55f8700024ba9d90003b65e7a'

        ref_id = ref_id.removeprefix("galaxy-")

        return tg_web_data, username.lower(), ref_id

    async def check_proxy(self, http_client: CloudflareScraper) -> bool:
        proxy_conn = http_client.connector
        if proxy_conn and not hasattr(proxy_conn, '_proxy_host'):
            logger.info(f"{self.session_name} | Running Proxy-less.")
            return True
        try:
            response = await http_client.get(url='https://ifconfig.me/ip', timeout=aiohttp.ClientTimeout(15))
            logger.info(f"{self.session_name} | Proxy IP: {await response.text()}.")
            return True
        except Exception as error:
            proxy_url = f"{proxy_conn._proxy_type}://{proxy_conn._proxy_host}:{proxy_conn._proxy_port}"
            log_error(f"{self.session_name} | Proxy: {proxy_url} | Error: {type(error).__name__}.")
            return False

    async def run(self) -> None:
        api = TverseAPI(self.app_version)
        random_delay = randint(settings.START_DELAY[0], settings.START_DELAY[1])
        logger.info(f"{self.session_name} | Bot will start in <ly>{int(random_delay)}s</ly>.")
        await asyncio.sleep(random_delay)

        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
        proxy_conn = ProxyConnector.from_url(self.proxy, ssl=ssl_context) if self.proxy \
            else aiohttp.TCPConnector(ssl_context=ssl_context)
        async with CloudflareScraper(headers=self.headers, timeout=aiohttp.ClientTimeout(60), connector=proxy_conn) as http_client:
            while True:
                if settings.NIGHT_MODE:
                    current_utc_time = datetime.datetime.utcnow().time()

                    start_time = datetime.time(settings.NIGHT_TIME[0], 0)
                    end_time = datetime.time(settings.NIGHT_TIME[1], 0)

                    next_checking_time = randint(settings.NIGHT_CHECKING[0], settings.NIGHT_CHECKING[1])

                    if start_time <= current_utc_time <= end_time:
                        logger.info(f"{self.session_name} | Night-Mode is on, The current UTC time is {current_utc_time.replace(microsecond=0)}, next check-in on {round(next_checking_time / 3600, 1)} hours.")
                        await asyncio.sleep(next_checking_time)
                        continue
                
                if not await self.check_proxy(http_client=http_client):
                    logger.warning(f"{self.session_name} | Failed to connect to proxy server. Sleep 5 minutes.")
                    await asyncio.sleep(300)
                    continue
                
                tg_web_data, username, ref_id = await self.get_tg_web_data()

                sleep_time = randint(settings.SLEEP_TIME[0], settings.SLEEP_TIME[1])

                try:
                    if not tg_web_data:
                        logger.warning(f"{self.session_name} | Failed to get Web-View Data. Retrying in 5 minutes.")
                        await asyncio.sleep(300)
                        continue

                    self.auth_token = get_token(self.session_name)

                    if self.auth_token is None:
                        login_data = await api.login(http_client, init_data=tg_web_data)

                        if not login_data:
                            logger.warning(f"{self.session_name} | Failed to get Login Data. Retrying in 5 minutes.")
                            await asyncio.sleep(300)
                            continue

                        if login_data.get("error", {}).get("baninfo"):
                            append_token(name=self.session_name, auth=None)
                            await asyncio.sleep(1)
                            raise AuthError(f"{self.session_name} | Account Banned")
                        
                        self.auth_token = login_data.get("response", {}).get("session")
                        append_token(name=self.session_name, auth=self.auth_token)
                    
                    # User Data
                    user_data = await api.user_data(http_client, session_token=self.auth_token)
                    if not user_data:
                        logger.warning(f"{self.session_name} | Failed to get User Data. Retrying in 5 minutes.")
                        await asyncio.sleep(300)
                        continue

                    if user_data.get("error", {}).get("baninfo"):
                        append_token(name=self.session_name, auth=None)
                        raise AuthError(f"{self.session_name} | Account Banned")

                    if user_data.get("error", {}).get('text') == "Permission denied":
                        append_token(name=self.session_name, auth=None)
                        logger.warning(f"{self.session_name} | Invalid Auth Token. Retrying in 5 minutes.")
                        await asyncio.sleep(300)
                        continue

                    logger.success(f"{self.session_name} | <g>🪐 Login Successful</g>")
                    await asyncio.sleep(2)
                    
                    total_galaxy = user_data['response'].get('galaxy') or 0
                    total_dust = user_data['response'].get('dust_max') or 0
                    current_dust = user_data['response'].get('dust') or 0
                    awards = user_data['response'].get('awards') or 0

                    allow_scan = user_data['response'].get('is_scan_available') or False
                    scan_chance = float(user_data['response']['effects'].get('scan_chance')) or 0
                    
                    logger.info(f"{self.session_name} | Galaxy: <y>{total_galaxy}</y> | Total Dust: <y>({current_dust}/{total_dust})</y> | Achievements: <y>{awards}</y>")
                    await asyncio.sleep(random.randint(1, 3))

                    # Create Galaxy
                    if total_galaxy <= 0:
                        logger.info(f"{self.session_name} | Creating Galaxy...")
                        create_galaxy = await api.begin_galaxy(http_client, session_token=self.auth_token, stars=100, referral=ref_id)

                        if not create_galaxy:
                            logger.warning(f"{self.session_name} | Failed to Create Galaxy. Retrying in 5 minutes.")
                            await asyncio.sleep(300)
                            continue

                        logger.success(f"{self.session_name} | Galaxy has been successfully created.")
                        await asyncio.sleep(random.randint(1, 3))

                    # Galaxy Data
                    galaxy_data = await api.get_galaxy(http_client, session_token=self.auth_token)

                    if not galaxy_data:
                        logger.warning(f"{self.session_name} | Failed to get Galaxy Data. Retrying in 5 minutes.")
                        await asyncio.sleep(300)
                        continue

                    total_stars = galaxy_data['response'].get('stars') or 0
                    total_max_stars = galaxy_data['response'].get('stars_max') or 0
                    galaxy_name = galaxy_data['response'].get('title') or None
                    created_on = int(galaxy_data['response'].get('created')) or 946684800
                    galaxy_day = unix_convert(created_on)
                    galaxy_id = galaxy_data['response'].get('id') or None

                    scan_stat = galaxy_data['response'].get('scan') or None 
                    civilization = int(galaxy_data['response'].get('civilization')) or 0

                    logger.info(f"{self.session_name} | Current Galaxy: <y>{galaxy_name}</y> | Stars: <y>({total_stars}/{total_max_stars})</y> | Created on: <y>{galaxy_day}</y>")
                    await asyncio.sleep(random.randint(1, 3))
                    
                    # Scan Results
                    if scan_stat is not None:
                        scan_exp = int(scan_stat.get('expires'))
                        if int(time()) > scan_exp:
                            scan_result = await api.scan_result(http_client, session_token=self.auth_token, galaxy_id=galaxy_id)

                            if not scan_result:
                                logger.warning(f"{self.session_name} | Failed to get Scan Results. Retrying in 5 minutes.")
                                await asyncio.sleep(300)
                                continue

                            cscan = scan_result['response'].get('scan_result') or None
                            if cscan == None:
                                logger.info(f"{self.session_name} | Scan Results: No Civilizations Found.")
                            else:
                                logger.success(f"{self.session_name} | Scan Results: <g>Civilizations Found.</g>")

                    await asyncio.sleep(random.randint(1, 3))

                    # Auto Scan
                    if settings.AUTO_SCAN and allow_scan and scan_stat is None:
                        scan_power = math.floor(int(current_dust) / 10000)

                        scan_status = await api.scan_status(http_client, session_token=self.auth_token)
                        if scan_status:
                            if scan_power >= 1:
                                success_chance = calc_scan_chance(scan_power, total_stars, scan_chance)

                                if success_chance > settings.SCAN_PERCENTAGE:
                                    scan_data = await api.scan_start(http_client, session_token=self.auth_token, galaxy_id=galaxy_id, power=scan_power)

                                    if not scan_data:
                                        logger.warning(f"{self.session_name} | Failed to get Scan Data. Retrying in 5 minutes.")
                                        await asyncio.sleep(300)
                                        continue

                                    logger.success(f"{self.session_name} | Scan Started: {scan_power}PW ~{success_chance}% Success Chance.")

                    await asyncio.sleep(random.randint(1, 3))

                    # Auto Redeem Gift
                    if settings.AUTO_REDEEM_CODE:
                        gift_code = getGiftCode(username.lower())
                        if gift_code:
                            logger.info(f"{self.session_name} | Total Gift-Codes for <y>@{username}</y>: <y>{len(gift_code)}</y>. Initiating redemption...")

                            successful_activations = 0

                            for code in gift_code:
                                code_info = await api.get_gift(http_client, session_token=self.auth_token, gift_id=code)
                                if not code_info:
                                    logger.warning(f"{self.session_name} | Failed to get Code Info. Retrying in 5 minutes.")
                                    await asyncio.sleep(300)
                                    continue
                                
                                if code_info.get("response", {}).get("available") == False:
                                    logger.error(f"{self.session_name} | Skipping Code: <y>{code}</y> is Used. Check 'gift-codes.json' for more info.")
                                    errorGiftCode(code, 'used')
                                    continue

                                if code_info.get("error", {}).get("code") == 10010:
                                    logger.error(f"{self.session_name} | Skipping Code: <y>{code}</y> is Incorrect/Invalid. Check 'gift-codes.json' for more info.")
                                    errorGiftCode(code, 'incorrect')
                                    continue
                                
                                code_value = int(code_info['response'].get('value')) or 0
                                code_sender = code_info['response'].get('sender') or None

                                if code_info.get("response", {}).get("available") == True:
                                    redeem_data = await api.redeem_gift(http_client, session_token=self.auth_token, gift_id=code)

                                    if redeem_data.get("error", {}).get("code") == 10010:
                                        logger.error(f"{self.session_name} | Skipping Code: <y>{code}</y>, Code is incorrect or self-made. Check 'gift-codes.json' for more info.")
                                        errorGiftCode(code, 'incorrect')
                                        continue
                                    if not redeem_data:
                                        logger.warning(f"{self.session_name} | Failed to Redeem Code. Retrying in 5 minutes.")
                                        await asyncio.sleep(300)
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
                        user_data = await api.user_data(http_client, session_token=self.auth_token)
                        if not user_data:
                            logger.warning(f"{self.session_name} | Failed to get User Data. Retrying in 5 minutes.")
                            await asyncio.sleep(300)
                            continue

                        dust_progress = float(user_data['response'].get('dust_progress')) or 0

                        if dust_progress > 0:
                            logger.info(f"{self.session_name} | Collecting Dust...")
                            collect_dust = await api.collect_dust(http_client, session_token=self.auth_token)
                            if not collect_dust:
                                logger.warning(f"{self.session_name} | Failed to collect Star Dust. Retrying in 5 minutes.")
                                await asyncio.sleep(300)
                                continue

                            dust_collected = collect_dust['response'].get('dust') or 0
                            logger.success(f"{self.session_name} | Dust collected: <g>+{dust_collected}</g>")
                            
                        await asyncio.sleep(random.randint(1, 3))
                    
                    # Auto Create Stars
                    if settings.AUTO_CREATE_STAR:
                        star_allowed_username = [item.replace('@', '').lower() for item in settings.MAKE_STARS_ALLOWED_USERNAME]
                        star_restrict_username = [item.replace('@', '').lower() for item in settings.MAKE_STARS_RESTRICT_USERNAME]
                        
                        if (username in star_allowed_username or 'all' in star_allowed_username) and username not in star_restrict_username:
                            user_data = await api.user_data(http_client, session_token=self.auth_token)
                            if not user_data:
                                logger.warning(f"{self.session_name} | Failed to get User Data. Retrying in 5 minutes.")
                                await asyncio.sleep(300)
                                continue
                            
                            current_dust = int(user_data['response'].get('dust')) or 0
                            total_dust = int(user_data['response'].get('dust_max')) or 0
                            
                            current_stars = int(user_data['response'].get('stars')) or 0
                            total_stars = int(user_data['response'].get('stars_max')) or 0
                            
                            if settings.USE_DUST_PERCENTAGE == 0:
                                dust_available = current_dust
                            else:
                                dust_available = (settings.USE_DUST_PERCENTAGE / 100) * total_dust
                            
                            if current_dust >= dust_available:
                                dustnow = current_dust
                                stars_value = stars_count(current_dust, current_stars)

                                if stars_value > 100:
                                    logger.info(f"{self.session_name} | Creating <y>{stars_value}</y> stars...")
                                    if galaxy_id:
                                        stars_data = await api.create_stars(http_client, session_token=self.auth_token, galaxy_id=galaxy_id, stars=stars_value)
                                        if stars_data:
                                            logger.success(f"{self.session_name} | Stars Created: <g>+{stars_value}</g>")
                                            logger.info(f"{self.session_name} | Updated Dust: <y>({int(dustnow - current_dust)}/{total_dust})</y> | Updated Stars: <y>({current_stars + stars_value}/{total_stars})</y>")
                                    else:
                                        logger.error(f"{self.session_name} | Unable to find Galaxy-ID, Can not create Stars!")

                        await asyncio.sleep(random.randint(1, 3))

                    # Apply Boost
                    if settings.AUTO_APPLY_BOOST:
                        boost_data = await api.get_boost(http_client, session_token=self.auth_token)
                        if not boost_data:
                            logger.warning(f"{self.session_name} | Failed to get Boost Data. Retrying in 5 minutes.")
                            await asyncio.sleep(300)
                            continue
                        
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
                                    boost_count = boostCount(total=count)
                                    apply_boost = await api.activate_boost(http_client, session_token=self.auth_token, boost_id=boost_id, boost_count=boost_count)
                                    if not apply_boost:
                                        logger.warning(f"{self.session_name} | Failed to Apply Data. Retrying in 5 minutes.")
                                        await asyncio.sleep(300)
                                        continue
                                    
                                    logger.success(f"{self.session_name} | Boost Activated: <g>{boost_count} hours ({self.boost_translation.get(boost_id, 'N/A')})</g>")
                                
                                if boost_id == 3:
                                    boost_delay = max(boost_delay, boost_count * 60 * 60)
                                
                                await asyncio.sleep(random.randint(1, 3))
                        if boost_delay > 0:
                            adjusted_sleep = boost_delay + random.randint(settings.EXTRA_BOOST_DELAY[0], settings.EXTRA_BOOST_DELAY[1]) - sleep_time
                            if adjusted_sleep > 0:
                                hours, minutes = divmod(adjusted_sleep // 60, 60)
                                logger.info(f"{self.session_name} | Sleep <y>{hours} hour, {minutes} mins</y>; due to auto-collect boost.")
                                await asyncio.sleep(adjusted_sleep)

                    logger.info(f"{self.session_name} | Sleeping <y>{round(sleep_time / 60, 1)}</y> min.")
                    await asyncio.sleep(delay=sleep_time)

                except InvalidSession:
                    raise
                except Exception as error:
                    log_error(f"{self.session_name} | Unknown error: {error}. Sleeping <y>{round(sleep_time / 60, 1)}</y> min.")
                    await asyncio.sleep(delay=sleep_time)

async def run_tapper(tg_client: UniversalTelegramClient, app_id: str):
    runner = Tapper(tg_client=tg_client, app_id=app_id)
    try:
        await runner.run()
    except InvalidSession as e:
        session_file = f"{SESSIONS_PATH}/{tg_client.session_name}.session"
        if not os.path.exists(f"{SESSIONS_PATH}/deleted_sessions"):
            os.makedirs(f"{SESSIONS_PATH}/deleted_sessions", exist_ok=True)
        shutil.move(session_file, f"{SESSIONS_PATH}/deleted_sessions/{tg_client.session_name}.session")
        logger.error(f"Invalid Session: {e}. Moved to `deleted_sessions`.")
    except AuthError as e:
        logger.error(e)
