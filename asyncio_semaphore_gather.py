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
    # One shared semaphore controls access across every fetch() coroutine.
    # Semaphore(3) means at most three coroutines can hold a permit at once,
    # so no more than three HTTP requests may be in flight concurrently.
    #
    # The semaphore does NOT limit how many coroutines can exist or be
    # scheduled; it only limits entry into the protected section inside fetch().
    semaphore = asyncio.Semaphore(3)

    async with httpx.AsyncClient(timeout=10) as client:
        # All coroutines share the same semaphore instance, so they compete
        # for the same pool of three permits. Creating these coroutine objects
        # does not itself start the requests.
        coroutines = [fetch(client, delay, semaphore) for delay in delays]
        # gather() schedules the coroutines concurrently and waits for the
        # whole group to finish. The semaphore independently limits how many
        # may execute the HTTP-request section at the same time.
        #
        # These are separate concerns:
        # gather()    -> coordinates the group and preserves input/result order
        # semaphore   -> limits concurrency inside the guarded section
        #
        # So even if the fetches complete in a different order, gather()
        # returns results in the same order as the input coroutines:
        # 6, 3, 1, 0, 4, 5, 2.
        #
        # If we used asyncio.as_completed() instead, the semaphore behaviour
        # would stay the same, but results would be consumed in completion
        results = await asyncio.gather(*coroutines)

    print(results)
    total = time.perf_counter() - start
    print(f"Script total run time: {total:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(main())