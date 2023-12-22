import asyncio

from db_create import async_main
from db_fill import run

if __name__ == '__main__':
    asyncio.run(async_main())
    asyncio.run(run())
