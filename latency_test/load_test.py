# import asyncio
# import aiohttp
# import time
# import statistics
# import numpy as np

# URL = "https://v2-api.fordgeindia.online/api/portfolio/public/aadhya-shopping/meta/"
# # URL = "https://aadhya-shopping.fordgeindia.online/"

# CONCURRENT_USERS = 25    # simulate users at once
# TEST_DURATION = 30         # seconds
# REQUEST_TIMEOUT = 10       # seconds


# class Stats:
#     def __init__(self):
#         self.latencies = []
#         self.success = 0
#         self.failures = 0

#     def report(self):
#         if not self.latencies:
#             print("No successful requests")
#             return

#         latencies_ms = [l * 1000 for l in self.latencies]

#         print("\n========== LOAD TEST REPORT ==========")
#         print(f"Total Requests   : {len(self.latencies) + self.failures}")
#         print(f"Successful       : {self.success}")
#         print(f"Failed           : {self.failures}")
#         print(f"Requests/sec     : {self.success / TEST_DURATION:.2f}")
#         print(f"Avg Latency (ms) : {statistics.mean(latencies_ms):.2f}")
#         print(f"P50 Latency (ms) : {np.percentile(latencies_ms, 50):.2f}")
#         print(f"P90 Latency (ms) : {np.percentile(latencies_ms, 90):.2f}")
#         print(f"P95 Latency (ms) : {np.percentile(latencies_ms, 95):.2f}")
#         print(f"P99 Latency (ms) : {np.percentile(latencies_ms, 99):.2f}")
#         print("=====================================\n")


# async def worker(session, stats: Stats, stop_time: float):
#     while time.time() < stop_time:
#         start = time.perf_counter()
#         try:
#             async with session.get(URL) as resp:
#                 if resp.status == 200:
#                     await resp.read()
#                     latency = time.perf_counter() - start
#                     stats.latencies.append(latency)
#                     stats.success += 1
#                 else:
#                     stats.failures += 1
#         except Exception:
#             stats.failures += 1


# async def run_test():
#     stats = Stats()
#     timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
#     connector = aiohttp.TCPConnector(limit=0)  # unlimited sockets

#     async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
#         stop_time = time.time() + TEST_DURATION
#         tasks = [
#             asyncio.create_task(worker(session, stats, stop_time))
#             for _ in range(CONCURRENT_USERS)
#         ]
#         await asyncio.gather(*tasks)

#     stats.report()


# if __name__ == "__main__":
#     asyncio.run(run_test())

import asyncio
import aiohttp
import time

URLS = [
    "https://v2-api.fordgeindia.online/api/portfolio/public/aadhya-shopping/meta/",
    "https://v2-api.fordgeindia.online/api/portfolio/public/aadhya-shopping/categories/?v=1767181780",
    "https://v2-api.fordgeindia.online/api/portfolio/public/aadhya-shopping/products/?page=1&page_size=10&search=&min_price=&max_price=&category=&v=1767181780",
    "https://v2-api.fordgeindia.online/api/portfolio/public/aadhya-shopping/collections/",
]

async def fetch(session, url):
    start = time.perf_counter()
    async with session.get(url) as resp:
        await resp.read()
    return url, (time.perf_counter() - start) * 1000

async def main():
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        start = time.perf_counter()
        results = await asyncio.gather(*[fetch(session, u) for u in URLS])
        total = (time.perf_counter() - start) * 1000

    print("\n=== API PARALLEL TEST ===")
    for url, t in results:
        print(f"{url}\n  -> {t:.2f} ms\n")
    print(f"TOTAL (parallel): {total:.2f} ms")

asyncio.run(main())

