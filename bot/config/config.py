from pydantic_settings import BaseSettings, SettingsConfigDict
from bot.utils import logger
import sys

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int = 1234
    API_HASH: str = 'abcd'
    
    SUPPORT_AUTHOR: bool = True
    
    AUTO_COLLECT_DUST: bool = True
    
    AUTO_APPLY_BOOST: bool = True
    EXTRA_BOOST_DELAY: list[int] = [100, 500]
    
    AUTO_REDEEM_CODE: bool = True
    
    AUTO_CREATE_STAR: bool = False
    USE_DUST_PERCENTAGE: int = 90
    SLIDER_STARS_VALUE: bool = True
    MAKE_STARS_ALLOWED_USERNAME: list[str] = ["all"]
    MAKE_STARS_RESTRICT_USERNAME: list[str] = []
    
    AUTO_COLLECT_NEEDLE: bool = True
    MAX_SEARCH_TRIES: int = 15

    SLEEP_TIME: list[int] = [2700, 4200]
    START_DELAY: list[int] = [5, 100]
    
    REF_KEY: str = 'galaxy-0003f55f8700024ba9d90003b65e7a'
    IN_USE_SESSIONS_PATH: str = 'bot/config/used_sessions.txt'
    
    NIGHT_MODE: bool = False
    NIGHT_TIME: list[int] = [0, 7] #TIMEZONE = UTC, FORMAT = HOURS, [start, end]
    NIGHT_CHECKING: list[int] = [3600, 7200]
    
    SAVE_RESPONSE_DATA: bool = False
    MAX_REQUEST_RETRY: int = 3
    TRACK_BOT_UPDATES: bool = True

settings = Settings()

if settings.API_ID == 1234 and settings.API_HASH == 'abcd':
    sys.exit(logger.info("<r>Please edit API_ID and API_HASH from .env file to continue.</r>"))

if settings.API_ID == 1234:
    sys.exit(logger.info("Please edit API_ID from .env file to continue."))

if settings.API_HASH == 'abcd':
    sys.exit(logger.info("Please edit API_HASH from .env file to continue."))