import asyncio
import os
from better_proxy import Proxy
from datetime import datetime, timedelta
from random import randint, uniform
from sqlite3 import OperationalError
from typing import Union

from opentele.tl import TelegramClient
from telethon.errors import *
from telethon.functions import messages, channels, account
from telethon.network import ConnectionTcpAbridged
from telethon.types import InputBotAppShortName, InputPeerNotifySettings, InputNotifyPeer, InputUser

import pyrogram.raw.functions.account as paccount
import pyrogram.raw.functions.channels as pchannels
import pyrogram.raw.functions.messages as pmessages
from pyrogram import Client as PyrogramClient
from pyrogram.errors import *
from pyrogram.raw import types as ptypes

from bot.config import settings
from bot.exceptions import InvalidSession
from bot.utils.proxy_utils import to_pyrogram_proxy, to_telethon_proxy
from bot.utils import logger, log_error, AsyncInterProcessLock, CONFIG_PATH, first_run


class UniversalTelegramClient:
    def __init__(self, **client_params):
        self.session_name = None
        self.client: Union[TelegramClient, PyrogramClient]
        self.proxy = None
        self.is_fist_run = True
        self.is_pyrogram: bool = False
        self._client_params = client_params
        self._init_client()

        self.lock = AsyncInterProcessLock(
            os.path.join(os.path.dirname(CONFIG_PATH), 'lock_files', f"{self.session_name}.lock"))

        self._webview_data = None

    def _init_client(self):
        try:
            self.client = TelegramClient(connection=ConnectionTcpAbridged, **self._client_params)
            self.is_pyrogram = False
            self.session_name, _ = os.path.splitext(os.path.basename(self.client.session.filename))
        except OperationalError:
            session_name = self._client_params.pop('session')
            self._client_params.pop('system_lang_code')
            self._client_params['name'] = session_name
            self.client = PyrogramClient(**self._client_params)
            self.is_pyrogram = True
            self.session_name, _ = os.path.splitext(os.path.basename(self.client.name))

    def set_proxy(self, proxy: Proxy):
        if self.is_pyrogram is False:
            self.proxy = to_telethon_proxy(proxy)
            self.client.set_proxy(self.proxy)
        else:
            self.proxy = to_pyrogram_proxy(proxy)
            self.client.proxy = self.proxy

    async def get_app_webview_url(self, bot_username: str, bot_shortname: str, default_val: str) -> str:
        self.is_fist_run = await first_run.check_is_first_run(self.session_name)
        return await self._pyrogram_get_app_webview_url(bot_username, bot_shortname, default_val) if self.is_pyrogram \
            else await self._telethon_get_app_webview_url(bot_username, bot_shortname, default_val)

    async def get_webview_url(self, bot_username: str, bot_url: str, default_val: str) -> str:
        self.is_fist_run = await first_run.check_is_first_run(self.session_name)
        return await self._pyrogram_get_webview_url(bot_username, bot_url, default_val) if self.is_pyrogram \
            else await self._telethon_get_webview_url(bot_username, bot_url, default_val)

    async def join_and_mute_tg_channel(self, link: str):
        return await self._pyrogram_join_and_mute_tg_channel(link) if self.is_pyrogram \
            else await self._telethon_join_and_mute_tg_channel(link)

    async def update_profile(self, first_name: str = None, last_name: str = None, about: str = None):
        return await self._pyrogram_update_profile(first_name=first_name, last_name=last_name, about=about) if self.is_pyrogram \
            else await self._telethon_update_profile(first_name=first_name, last_name=last_name, about=about)

    async def _telethon_initialize_webview_data(self, bot_username: str, bot_shortname: str = None):
        if not self._webview_data:
            while True:
                try:
                    peer = await self.client.get_input_entity(bot_username)
                    bot_id = InputUser(user_id=peer.user_id, access_hash=peer.access_hash)
                    input_bot_app = InputBotAppShortName(bot_id=bot_id, short_name=bot_shortname)
                    self._webview_data = {'peer': peer, 'app': input_bot_app} if bot_shortname \
                        else {'peer': peer, 'bot': peer}
                    return
                except FloodWaitError as fl:
                    logger.warning(f"<ly>{self.session_name}</ly> | FloodWait {fl}. Waiting {fl.seconds}s")
                    await asyncio.sleep(fl.seconds + 3)

    async def _telethon_get_app_webview_url(self, bot_username: str, bot_shortname: str, default_val: str) -> str:
        if self.proxy and not self.client._proxy:
            logger.critical(f"<ly>{self.session_name}</ly> | Proxy found, but not passed to TelegramClient")
            exit(-1)

        async with self.lock:
            try:
                if not self.client.is_connected():
                    await self.client.connect()
                await self._telethon_initialize_webview_data(bot_username=bot_username, bot_shortname=bot_shortname)
                await asyncio.sleep(uniform(1, 2))

                start = {'start_param': settings.REF_ID if randint(0, 100) <= 85 and settings.REF_ID else default_val} if self.is_fist_run else {}

                web_view = await self.client(messages.RequestAppWebViewRequest(
                    **self._webview_data,
                    platform='android',
                    write_allowed=True,
                    **start
                ))

                return web_view.url

            except (UnauthorizedError, AuthKeyUnregisteredError):
                raise InvalidSession(f"{self.session_name}: User is unauthorized")
            except (UserDeactivatedError, UserDeactivatedBanError, PhoneNumberBannedError):
                raise InvalidSession(f"{self.session_name}: User is banned")

            except Exception:
                raise

            finally:
                if self.client.is_connected():
                    await self.client.disconnect()
                    await asyncio.sleep(15)

    async def _telethon_get_webview_url(self, bot_username: str, bot_url: str, default_val: str) -> str:
        if self.proxy and not self.client._proxy:
            logger.critical(f"<ly>{self.session_name}</ly> | Proxy found, but not passed to TelegramClient")
            exit(-1)

        async with self.lock:
            try:
                if not self.client.is_connected():
                    await self.client.connect()
                await self._telethon_initialize_webview_data(bot_username=bot_username)
                await asyncio.sleep(uniform(1, 2))

                default_val = default_val.removeprefix("galaxy-")
                REF_ID = settings.REF_ID if randint(0, 100) <= 85 and settings.REF_ID else default_val
                start = {'start_param': REF_ID} if self.is_fist_run else {}

                start_state = False
                async for message in self.client.iter_messages(bot_username):
                    if r'/start' in message.text:
                        start_state = True
                        break
                await asyncio.sleep(uniform(0.5, 1))
                if not start_state:
                    await self.client(messages.StartBotRequest(**self._webview_data, **start))
                await asyncio.sleep(uniform(1, 2))

                web_view = await self.client(messages.RequestWebViewRequest(
                    **self._webview_data,
                    platform='android',
                    from_bot_menu=False,
                    url=bot_url,
                    **start
                ))

                return web_view.url

            except (UnauthorizedError, AuthKeyUnregisteredError):
                raise InvalidSession(f"{self.session_name}: User is unauthorized")
            except (UserDeactivatedError, UserDeactivatedBanError, PhoneNumberBannedError):
                raise InvalidSession(f"{self.session_name}: User is banned")

            except Exception:
                raise

            finally:
                if self.client.is_connected():
                    await self.client.disconnect()
                    await asyncio.sleep(15)

    async def _pyrogram_initialize_webview_data(self, bot_username: str, bot_shortname: str = None):
        if not self._webview_data:
            while True:
                try:
                    peer = await self.client.resolve_peer(bot_username)
                    input_bot_app = ptypes.InputBotAppShortName(bot_id=peer, short_name=bot_shortname)
                    self._webview_data = {'peer': peer, 'app': input_bot_app} if bot_shortname \
                        else {'peer': peer, 'bot': peer}
                    return
                except FloodWait as fl:
                    logger.warning(f"<ly>{self.session_name}</ly> | FloodWait {fl}. Waiting {fl.value}s")
                    await asyncio.sleep(fl.value + 3)

    async def _pyrogram_get_app_webview_url(self, bot_username: str, bot_shortname: str, default_val: str) -> str:
        if self.proxy and not self.client.proxy:
            logger.critical(f"<ly>{self.session_name}</ly> | Proxy found, but not passed to Client")
            exit(-1)

        async with self.lock:
            try:
                if not self.client.is_connected:
                    await self.client.connect()
                await self._pyrogram_initialize_webview_data(bot_username, bot_shortname)
                await asyncio.sleep(uniform(1, 2))

                start = {'start_param': settings.REF_ID if randint(0, 100) <= 85 and settings.REF_ID else default_val} if self.is_fist_run else {}
                web_view = await self.client.invoke(pmessages.RequestAppWebView(
                    **self._webview_data,
                    platform='android',
                    write_allowed=True,
                    **start
                ))

                return web_view.url

            except (Unauthorized, AuthKeyUnregistered):
                raise InvalidSession(f"{self.session_name}: User is unauthorized")
            except (UserDeactivated, UserDeactivatedBan, PhoneNumberBanned):
                raise InvalidSession(f"{self.session_name}: User is banned")

            except Exception:
                raise

            finally:
                if self.client.is_connected:
                    await self.client.disconnect()
                    await asyncio.sleep(15)

    async def _pyrogram_get_webview_url(self, bot_username: str, bot_url: str, default_val: str) -> str:
        if self.proxy and not self.client.proxy:
            logger.critical(f"<ly>{self.session_name}</ly> | Proxy found, but not passed to Client")
            exit(-1)

        async with self.lock:
            try:
                if not self.client.is_connected:
                    await self.client.connect()
                await self._pyrogram_initialize_webview_data(bot_username)
                await asyncio.sleep(uniform(1, 2))

                default_val = default_val.removeprefix("galaxy-")
                REF_ID = settings.REF_ID if randint(0, 100) <= 85 and settings.REF_ID else default_val
                start = {'start_param': REF_ID} if self.is_fist_run else {}

                start_state = False
                async for message in self.client.get_chat_history(bot_username):
                    if r'/start' in message.text:
                        start_state = True
                        break
                await asyncio.sleep(uniform(0.5, 1))
                if not start_state:
                    await self.client.invoke(pmessages.StartBot(**self._webview_data,
                                                                random_id=randint(1, 2**63),
                                                                **start))
                await asyncio.sleep(uniform(1, 2))
                web_view = await self.client.invoke(pmessages.RequestWebView(
                    **self._webview_data,
                    platform='android',
                    from_bot_menu=False,
                    url=bot_url,
                    **start
                ))

                return web_view.url

            except (Unauthorized, AuthKeyUnregistered):
                raise InvalidSession(f"{self.session_name}: User is unauthorized")
            except (UserDeactivated, UserDeactivatedBan, PhoneNumberBanned):
                raise InvalidSession(f"{self.session_name}: User is banned")

            except Exception:
                raise

            finally:
                if self.client.is_connected:
                    await self.client.disconnect()
                    await asyncio.sleep(15)

    async def _telethon_join_and_mute_tg_channel(self, link: str):
        path = link.replace("https://t.me/", "")
        if path == 'money':
            return

        async with self.lock:
            async with self.client as client:
                try:
                    if path.startswith('+'):
                        invite_hash = path[1:]
                        result = await client(messages.ImportChatInviteRequest(hash=invite_hash))
                        channel_title = result.chats[0].title
                        entity = result.chats[0]
                    else:
                        entity = await client.get_entity(f'@{path}')
                        await client(channels.JoinChannelRequest(channel=entity))
                        channel_title = entity.title

                    await asyncio.sleep(1)

                    await client(account.UpdateNotifySettingsRequest(
                        peer=InputNotifyPeer(entity),
                        settings=InputPeerNotifySettings(
                            show_previews=False,
                            silent=True,
                            mute_until=datetime.today() + timedelta(days=365)
                        )
                    ))

                    logger.info(f"<ly>{self.session_name}</ly> | Subscribed to channel: <y>{channel_title}</y>")
                except FloodWaitError as fl:
                    logger.warning(f"<ly>{self.session_name}</ly> | FloodWait {fl}. Waiting {fl.seconds}s")
                    return fl.seconds
                except Exception as e:
                    log_error(
                        f"<ly>{self.session_name}</ly> | (Task) Error while subscribing to tg channel {link}: {e}")

            await asyncio.sleep(uniform(15, 20))
        return

    async def _pyrogram_join_and_mute_tg_channel(self, link: str):
        path = link.replace("https://t.me/", "")
        if path == 'money':
            return

        async with self.lock:
            async with self.client:
                try:
                    if path.startswith('+'):
                        invite_hash = path[1:]
                        result = await self.client.invoke(pmessages.ImportChatInvite(hash=invite_hash))
                        channel_title = result.chats[0].title
                        entity = result.chats[0]
                        peer = ptypes.InputPeerChannel(channel_id=entity.id, access_hash=entity.access_hash)
                    else:
                        peer = await self.client.resolve_peer(f'@{path}')
                        channel = ptypes.InputChannel(channel_id=peer.channel_id, access_hash=peer.access_hash)
                        await self.client.invoke(pchannels.JoinChannel(channel=channel))
                        channel_title = path

                    await asyncio.sleep(1)

                    await self.client.invoke(paccount.UpdateNotifySettings(
                        peer=ptypes.InputNotifyPeer(peer=peer),
                        settings=ptypes.InputPeerNotifySettings(
                            show_previews=False,
                            silent=True,
                            mute_until=2147483647))
                    )

                    logger.info(f"<ly>{self.session_name}</ly> | Subscribed to channel: <y>{channel_title}</y>")
                except FloodWait as e:
                    logger.warning(f"<ly>{self.session_name}</ly> | FloodWait {e}. Waiting {e.value}s")
                    return e.value
                except UserAlreadyParticipant:
                    logger.info(f"<ly>{self.session_name}</ly> | Was already Subscribed to channel: <y>{link}</y>")
                except Exception as e:
                    log_error(
                        f"<ly>{self.session_name}</ly> | (Task) Error while subscribing to tg channel {link}: {e}")

            await asyncio.sleep(uniform(15, 20))
        return

    async def _telethon_update_profile(self, first_name: str = None, last_name: str = None, about: str = None):
        update_params = {
            'first_name': first_name,
            'last_name': last_name,
            'about': about
        }
        update_params = {k: v for k, v in update_params.items() if v is not None}
        if not update_params:
            return

        async with self.lock:
            async with self.client:
                try:
                    await self.client(account.UpdateProfileRequest(**update_params))
                except Exception as e:
                    log_error(
                        f"<ly>{self.session_name}</ly> | Failed to update profile: {e}")
            await asyncio.sleep(uniform(15, 20))

    async def _pyrogram_update_profile(self, first_name: str = None, last_name: str = None, about: str = None):
        update_params = {
            'first_name': first_name,
            'last_name': last_name,
            'about': about
        }
        update_params = {k: v for k, v in update_params.items() if v is not None}
        if not update_params:
            return

        async with self.lock:
            async with self.client:
                try:
                    await self.client.invoke(paccount.UpdateProfile(**update_params))
                except Exception as e:
                    log_error(
                        f"<ly>{self.session_name}</ly> | Failed to update profile: {e}")
            await asyncio.sleep(uniform(15, 20))
