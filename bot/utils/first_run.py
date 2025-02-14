import aiofiles

async def check_is_first_run(session_name: str):
    async with aiofiles.open('first_run.txt', mode='a+') as file:
        await file.seek(0)
        lines = await file.readlines()
    return session_name.lower() not in [line.strip() for line in lines]


async def append_recurring_session(session_name: str):
    async with aiofiles.open('first_run.txt', mode='a+') as file:
        await file.writelines(session_name.lower() + '\n')
