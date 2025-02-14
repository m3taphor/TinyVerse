import asyncio
from contextlib import suppress
from bot.core.launcher import process
from os import system, name as os_name


def set_window_title(title):
    """ Set console window title cross-platform
    Args:
        title (str): New window title
    """
    if os_name == 'nt':
        system(f'title {title}')
    else:
        print(f'\033]0;{title}\007', end='', flush=True)


async def main():
    await process()


if __name__ == '__main__':
    set_window_title('TVerse (@UglyScripts)')
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
