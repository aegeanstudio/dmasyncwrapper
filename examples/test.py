# -*- coding: UTF-8 -*-
import asyncio
import time

import dmPython

from dmasyncwrapper import Pool, Cursor, init, close_all, with_dm
from dmasyncwrapper.consts import LocalCode

async_pool = Pool(
    host='localhost', port=5236, user='SYSDBA', password='Chn4ever1st',
    min_size=4, max_size=8, auto_commit=False, local_code=LocalCode.PG_UTF8)

connection = dmPython.connect(
    host='localhost', port=5236, user='SYSDBA', password='Chn4ever1st',
    autoCommit=False, local_code=LocalCode.PG_UTF8)


async def async_main():
    async with async_pool.acquire() as conn:
        for item in range(10000):
            async with conn.cursor() as cursor:
                await cursor.execute(
                    operation='SELECT * FROM SYS.DBA_USERS LIMIT ? OFFSET ?',
                    parameters=(1, 1))
                result = await cursor.fetchall()
                for row in result:
                    pass
            await conn.commit()


async def _async_concurrent_main():
        async with async_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    operation='SELECT * FROM SYS.DBA_USERS LIMIT ? OFFSET ?',
                    parameters=(1, 1))
                result = await cursor.fetchall()
                for row in result:
                    pass
            await conn.commit()


async def async_concurrent_main():
    tasks = [asyncio.create_task(_async_concurrent_main()) for _ in range(10000)]
    await asyncio.gather(*tasks)


def sync_main():
    with connection:
        for item in range(10000):
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM SYS.DBA_USERS LIMIT ? OFFSET ?', (1, 1))
                for row in cursor.fetchall():
                    pass
            connection.commit()


@with_dm(name='test', transaction=True)
async def _utils_each(cursor: Cursor):
    await cursor.execute(
        operation='SELECT * FROM SYS.DBA_USERS LIMIT ? OFFSET ?',
        parameters=(1, 1))
    result = await cursor.fetchall()
    for row in result:
        pass


async def async_utils_main():
    await init(
        pool_name='test', host='localhost', port=5236, user='SYSDBA',
        password='Chn4ever1st',
        auto_commit=False, local_code=LocalCode.PG_UTF8,
        min_size=4, max_size=8)
    coroutines = [_utils_each() for _ in range(10000)]
    await asyncio.gather(*coroutines)
    await close_all()


if __name__ == '__main__':
    sync_start_time = time.time()
    sync_main()
    connection.close()
    sync_end_time = time.time()
    print(f'Sync execution time: {sync_end_time - sync_start_time:.2f} seconds')

    async_start_time = time.time()
    asyncio.run(async_pool.init())
    asyncio.run(async_main())
    async_end_time = time.time()
    print(f'Async execution time: {async_end_time - async_start_time:.2f} seconds')

    async_concurrent_start_time = time.time()
    asyncio.run(async_concurrent_main())
    async_concurrent_end_time = time.time()
    print(f'Async concurrent execution time: {async_concurrent_end_time - async_concurrent_start_time:.2f} seconds')

    async_utils_start_time = time.time()
    asyncio.run(async_utils_main())
    async_utils_end_time = time.time()
    print(f'Async utils execution time: {async_utils_end_time - async_utils_start_time:.2f} seconds')

    asyncio.run(async_pool.close())
