import asyncio
import aiohttp
import time
import statistics

URL = "https://v2-api.fordgeindia.online/api/portfolio/public/aadhya-shopping/"

CONCURRENT_USERS = 50     # increase freely
REQUESTS_PER_USER = 20   # total requests = users × requests
TIMEOUT = 10


async def fetch(session, latencies):
    start = time.perf_counter()
    async with session.get(URL) as resp:
        await resp.read()
    latencies.append((time.perf_counter() - start) * 1000)


async def worker(session, latencies):
    for _ in range(REQUESTS_PER_USER):
        await fetch(session, latencies)


async def main():
    latencies = []
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    connector = aiohttp.TCPConnector(limit=0)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = [
            asyncio.create_task(worker(session, latencies))
            for _ in range(CONCURRENT_USERS)
        ]
        await asyncio.gather(*tasks)

    print("\n==== CACHED LOAD TEST ====")
    print(f"Total requests: {len(latencies)}")
    print(f"Avg latency  : {statistics.mean(latencies):.2f} ms")
    print(f"P50 latency  : {statistics.median(latencies):.2f} ms")
    print(f"P95 latency  : {statistics.quantiles(latencies, n=100)[94]:.2f} ms")
    print(f"P99 latency  : {statistics.quantiles(latencies, n=100)[98]:.2f} ms")
    print("==========================\n")


if __name__ == "__main__":
    asyncio.run(main())
