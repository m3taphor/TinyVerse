import asyncio
import argparse
from random import randint
from better_proxy import Proxy

from bot.utils import logger
from bot.core.tapper import run_tapper
from bot.core.registrator import register_sessions, get_tg_client
from bot.utils import build_check
from bot.utils.accounts import Accounts
from bot.utils.firstrun import load_session_names

def print_banner():
    print('''
    \033[38;5;128m╔=▄╥▄▄▄▄╗╗ ╥▄   ▄▄╥ ╥╔▄▄▄▄╥╗ ╥▄▄▄▄▄╥  ,▄φφφφφ▄, ╥╔▄▄▄▄╥╗\033[38;5;213m  ╔▄▄╥ \033[37m- (TVerse)
    \033[38;5;128m   |█▓'    ▓▓   ║▓╫ ▓▓N      ▓▓И  ╞▓▌ |╫▓   ┣▓┦ ▓▓N     \033[38;5;213m  [▓▓▌ 
    \033[38;5;128m    ▓█|    ╬▓   ┣▓╫ ▓█L,╥=,  ╫╫L_ Æ╣] ╘╨▓║P_  ' ▓█L,╥=, \033[38;5;213m  ╘║║╛ 
    \033[38;5;128m    ╫║     ┣▓▓__▓█╫ ║║Γ`""'  ▓▓Γ`┣▓   _     ▀█┳ ║║Γ`""' \033[38;5;213m   ▓▓  \033[37m- For education purpose
    \033[38;5;128m    █▓|     ╡╬▓▓╡╡  ▓▓_      ▓█   ╘█▌ ╫╪L   _█╫ ▓▓_     \033[38;5;213m   ▀▀  \033[37m- Version: 2.5 (accounts.json edition)
    \033[38;5;128m    ╘"'      "╘╘    ╘╘╘""""' ╘""   ╘╘  """""""  ╘╘╘""""'\033[38;5;213m   ╘╘  \033[37m- By [G.Hub]: \033[5m@m3taphor\033[38;5;135m
    \033[0m''')

    print('''                                             
-> Choose Option to continue (1/2):
    1. Run bot
    2. Create session

    ''')


def get_proxy(raw_proxy: str) -> Proxy:
    return Proxy.from_str(proxy=raw_proxy).as_url if raw_proxy else None


async def process() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", type=int, help="Action to perform (1/2)")
    action = parser.parse_args().action

    if not action:
        print_banner()

        while True:
            action = input("-> ")

            if not action.isdigit():
                logger.warning("Option must be number")
            elif action not in ["1", "2"]:
                logger.warning("Option must be 1 or 2")
            else:
                action = int(action)
                break

    used_session_names = load_session_names()

    if action == 2:
        await register_sessions()
    elif action == 1:
        accounts = await Accounts().get_accounts()
        await run_tasks(accounts=accounts, used_session_names=used_session_names)


async def run_tasks(accounts, used_session_names: str):
    await build_check.check_base_url()
    tasks = []
    for account in accounts:
        session_name, user_agent, raw_proxy = account.values()
        first_run = session_name not in used_session_names
        tg_client = await get_tg_client(session_name=session_name, proxy=raw_proxy)
        proxy = get_proxy(raw_proxy=raw_proxy)
        tasks.append(asyncio.create_task(run_tapper(tg_client=tg_client, user_agent=user_agent, proxy=proxy, first_run=first_run)))
        tasks.append(asyncio.create_task(build_check.check_bot_update_loop(2000)))
        await asyncio.sleep(randint(5, 20))

    await asyncio.gather(*tasks)
