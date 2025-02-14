from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True
    )

    API_ID: int = None
    API_HASH: str = None
    GLOBAL_CONFIG_PATH: str = "TG_FARM"

    FIX_CERT: bool = False

    START_DELAY: list[int] = [5, 100]
    SLEEP_TIME: list[int] = [2700, 4200]

    REF_ID: str = 'galaxy-0003f55f8700024ba9d90003b65e7a'

    AUTO_COLLECT_DUST: bool = True

    AUTO_CREATE_STAR: bool = False
    USE_DUST_PERCENTAGE: int = 90
    SLIDER_STARS_VALUE: bool = True
    MAKE_STARS_ALLOWED_USERNAME: list[str] = ["all"]
    MAKE_STARS_RESTRICT_USERNAME: list[str] = []

    AUTO_APPLY_BOOST: bool = True
    EXTRA_BOOST_DELAY: list[int] = [100, 500]

    AUTO_REDEEM_CODE: bool = False

    TRACK_BOT_UPDATES: bool = True

    NIGHT_MODE: bool = False
    NIGHT_TIME: list[int] = [0, 7] #TIMEZONE = UTC, FORMAT = HOURS, [start, end]
    NIGHT_CHECKING: list[int] = [3600, 7200]

    MAX_RETRY_REQUEST: int = 3
    DEVICE_PARAMS: bool = False
    DEBUG_LOGGING: bool = False
    SAVE_RESPONSE_DATA: bool = False

    SESSIONS_PER_PROXY: int = 1
    USE_PROXY: bool = True
    DISABLE_PROXY_REPLACE: bool = False

try:
    settings = Settings()
except ValidationError as e:
    print("Error: `.env` file seems to be invalid, Remove & create/copy again.")
    exit(-1)