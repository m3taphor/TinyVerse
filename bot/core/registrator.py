import os
from better_proxy import Proxy
from telethon import TelegramClient
from pyrogram import Client
from bot.config import settings
from bot.utils import logger, proxy_utils, config_utils, CONFIG_PATH, PROXIES_PATH, SESSIONS_PATH


API_ID = settings.API_ID
API_HASH = settings.API_HASH


async def register_sessions() -> None:
    if not API_ID or not API_HASH:
        raise ValueError("API_ID and API_HASH not found in the .env file.")

    session_name = input('\nEnter the session name (press Enter to exit): ').strip()
    if not session_name:
        return None

    session_file = f"{session_name}.session"
    device_params = {}

    if settings.DEVICE_PARAMS:
        logger.info("""
        Sample Device values (Don't use quotes):
        ### Attributes:
            device_model (`str`)     : `Samsung SM-G998B`
            system_version (`str`)   : `SDK 31`
            app_version (`str`)      : `8.4.1 (2522)`
        """)
        device_params.update(
            {
                'device_model': input('device_model: ').strip(),
                'system_version': input('system_version: ').strip(),
                'app_version': input('app_version: ').strip()
            }
        )
    accounts_config = config_utils.read_config_file(CONFIG_PATH)
    accounts_data = {
        "api": {
            'api_id': API_ID,
            'api_hash': API_HASH,
            **device_params
        }
    }
    proxy = None

    if settings.USE_PROXY:
        proxies = proxy_utils.get_unused_proxies(accounts_config, PROXIES_PATH)
        if not proxies:
            raise Exception('No unused proxies left')
        for prox in proxies:
            if await proxy_utils.check_proxy(prox):
                proxy_str = prox
                proxy = Proxy.from_str(proxy_str)
                accounts_data['proxy'] = proxy_str
                break
            else:
                raise Exception('No unused proxies left')
    else:
        accounts_data['proxy'] = None

    accounts_config[session_name] = accounts_data
    while True:
        res = input('-> Choose Session Type (1/2):\n    1. Telethon\n   2. Pyrogram\n').strip()
        if res not in ['1', '2']:
            logger.warning("Invalid option. Please enter 1 or 2")
        else:
            break
    if res == '1':
        session = TelegramClient(
            os.path.join(SESSIONS_PATH, session_file),
            api_id=API_ID,
            api_hash=API_HASH,
            lang_code="en",
            system_lang_code="en-US",
            **device_params
        )
        if proxy:
            logger.info(f"Using proxy: {proxy}")
            session.set_proxy(proxy_utils.to_telethon_proxy(proxy))

        await session.start()

        user_data = await session.get_me()

    else:
        session = Client(
            os.path.join(SESSIONS_PATH, session_file),
            api_id=API_ID,
            api_hash=API_HASH,
            lang_code="en",
            **device_params
        )
        if proxy:
            logger.info(f"Using proxy: {proxy}")
            session.proxy = proxy_utils.to_pyrogram_proxy(proxy)

        await session.start()

        user_data = await session.get_me()

    if user_data:
        await config_utils.write_config_file(accounts_config, CONFIG_PATH)
        logger.success(
            f'Session added successfully @{user_data.username} | {user_data.first_name} {user_data.last_name}'
        )
