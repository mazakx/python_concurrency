import asyncio
import httpx
import time
import threading

async def fetch(client: httpx.AsyncClient, delay: int, semaphore: asyncio.Semaphore) -> str:
    start = time.perf_counter()

    print(
        f"{threading.current_thread().name} "
        f"started delay = {delay}"
    )

    url = f"http://localhost:8080/delay/{delay}"

    async with semaphore:
        # This print happens only after the coroutine acquires a semaphore
        # permit, so it shows when the HTTP request actually starts.
        print(
            f"{threading.current_thread().name} "
            f"request started delay = {delay}"
        )

        response = await client.get(url)
        response.raise_for_status()
    
    print(
        f"{threading.current_thread().name} "
        f"finished delay = {delay}, "
        f"time taken = {time.perf_counter() - start:.4f} seconds"
    )

    return response.json()["url"]

async def main() -> None:
    start = time.perf_counter()
    delays = [6, 3, 1, 0, 4, 5, 2]
    results = []
    # One shared semaphore provides a pool of three permits for all fetch()
    # coroutines. It limits entry into the HTTP-request section; it does NOT
    # limit how many coroutine objects can exist or how many can be scheduled.
    semaphore = asyncio.Semaphore(3)

    async with httpx.AsyncClient(timeout=10) as client:
        # Calling fetch() creates raw coroutine objects. They are awaitable,
        # but are not independently scheduled merely by being created.
        coroutines = [fetch(client, delay, semaphore) for delay in delays]

        # as_completed() accepts an iterable of awaitables and schedules these
        # raw coroutine objects to run concurrently.
        #
        # Do not rely on their initial execution/start order matching the order
        # in 'delays'. as_completed() guarantees completion-order consumption,
        # not input-order startup.
        #
        # That matters here because whichever coroutines reach the semaphore
        # first compete for its three permits first. Semaphore admission order
        # therefore affects when each HTTP request is allowed to begin.
        #
        # Result order is determined by when each entire fetch() coroutine
        # finishes:
        #
        # task scheduled
        #     -> waits for semaphore permit
        #     -> HTTP request starts
        #     -> request finishes
        #     -> permit is released
        #     -> fetch() returns
        #     -> as_completed() exposes that result
        #
        # This means a shorter HTTP delay does not necessarily finish earlier.
        # A delay=1 coroutine may finish after delay=6 if it spends longer
        # waiting for a semaphore permit.
        for completed in asyncio.as_completed(coroutines):
            result = await completed
            results.append(result)

    print(results)
    total = time.perf_counter() - start
    print(f"Script total run time: {total:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(main())