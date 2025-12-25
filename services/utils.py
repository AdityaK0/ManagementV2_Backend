import asyncio

async def run_sqlite(fn):
    return await asyncio.to_thread(fn)