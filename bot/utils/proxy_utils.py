import os
import aiohttp
from aiohttp_proxy import ProxyConnector
from collections import Counter
from python_socks import ProxyType
from shutil import copyfile
from better_proxy import Proxy
from bot.config import settings
from bot.utils import logger
from random import shuffle

PROXY_TYPES = {
    'socks5': ProxyType.SOCKS5,
    'socks4': ProxyType.SOCKS4,
    'http': ProxyType.HTTP,
    'https': ProxyType.HTTP
}


def get_proxy_type(proxy_type: str):
    return PROXY_TYPES.get(proxy_type.lower())


def to_telethon_proxy(proxy: Proxy):
    return {
        'proxy_type': get_proxy_type(proxy.protocol),
        'addr': proxy.host,
        'port': proxy.port,
        'username': proxy.login,
        'password': proxy.password
    }


def to_pyrogram_proxy(proxy: Proxy):
    return {
                'scheme': proxy.protocol if proxy.protocol != 'https' else 'http',
                'hostname': proxy.host,
                'port': proxy.port,
                'username': proxy.login,
                'password': proxy.password
    }


def get_proxies(proxy_path: str) -> list[str]:
    """Reads proxies from the proxy file and returns array of proxies.
    If file doesn't exist, creates the file

     Args:
       proxy_path: Path to the proxies.txt file.

     Returns:
       The contents of the file, or an empty list if the file was empty or created.
     """
    proxy_template_path = "bot/config/proxies-template.txt"

    if not os.path.isfile(proxy_path):
        copyfile(proxy_template_path, proxy_path)
        return []

    if settings.USE_PROXY:
        with open(file=proxy_path, encoding="utf-8-sig") as file:
            return list({Proxy.from_str(proxy=row.strip()).as_url for row in file if row.strip() and
                         not row.strip().startswith('type')})
    else:
        return []


def get_unused_proxies(accounts_config, proxy_path: str):
    proxies_count = Counter([v.get('proxy') for v in accounts_config.values() if v.get('proxy')])
    all_proxies = get_proxies(proxy_path)
    return [proxy for proxy in all_proxies if proxies_count.get(proxy, 0) < settings.SESSIONS_PER_PROXY]


async def check_proxy(proxy):
    url = 'https://ifconfig.me/ip'
    proxy_conn = ProxyConnector.from_url(proxy)
    try:
        async with aiohttp.ClientSession(connector=proxy_conn, timeout=aiohttp.ClientTimeout(15)) as session:
            response = await session.get(url)
            if response.status == 200:
                logger.success(f"Successfully connected to proxy. IP: {await response.text()}")
                if not proxy_conn.closed:
                    proxy_conn.close()
                return True
    except Exception as e:
        logger.warning(f"Proxy {proxy} didn't respond")
        return False


async def get_proxy_chain(path) -> (str | None, str | None):
    try:
        with open(path, 'r') as file:
            proxy = file.read().strip()
            return proxy, to_telethon_proxy(Proxy.from_str(proxy))
    except Exception as e:
        logger.error(f"Failed to get proxy for proxy chain from '{path}'")
        return None, None


async def get_working_proxy(accounts_config: dict, current_proxy: str | None) -> str | None:
    if current_proxy and await check_proxy(current_proxy):
        return current_proxy

    from bot.utils import PROXIES_PATH
    unused_proxies = get_unused_proxies(accounts_config, PROXIES_PATH)
    shuffle(unused_proxies)
    for proxy in unused_proxies:
        if await check_proxy(proxy):
            return proxy

    return None
