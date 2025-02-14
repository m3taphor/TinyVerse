import os

from .logger import logger, log_error
from .async_lock import AsyncInterProcessLock
from . import proxy_utils, config_utils, first_run
from bot.config import settings


if not os.path.isdir(settings.GLOBAL_CONFIG_PATH):
    GLOBAL_CONFIG_PATH = os.environ.get(settings.GLOBAL_CONFIG_PATH, "")
else:
    GLOBAL_CONFIG_PATH = settings.GLOBAL_CONFIG_PATH
GLOBAL_CONFIG_EXISTS = os.path.isdir(GLOBAL_CONFIG_PATH)

CONFIG_PATH = os.path.join(GLOBAL_CONFIG_PATH, 'accounts_config.json') if GLOBAL_CONFIG_EXISTS else 'bot/config/accounts_config.json'
SESSIONS_PATH = os.path.join(GLOBAL_CONFIG_PATH, 'sessions') if GLOBAL_CONFIG_EXISTS else 'sessions'
PROXIES_PATH = os.path.join(GLOBAL_CONFIG_PATH, 'proxies.txt') if GLOBAL_CONFIG_EXISTS else 'bot/config/proxies.txt'
TOKENS_PATH = os.path.join(GLOBAL_CONFIG_PATH, 'auth_token.json') if GLOBAL_CONFIG_EXISTS else 'sessions/auth_token.json'

if not os.path.exists(path=SESSIONS_PATH):
    os.mkdir(path=SESSIONS_PATH)

if settings.FIX_CERT:
    from certifi import where
    os.environ['SSL_CERT_FILE'] = where()
