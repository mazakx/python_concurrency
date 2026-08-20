import asyncio
import httpx
import time
import threading

async def fetch(client: httpx.AsyncClient, delay: int) -> str:
    start = time.perf_counter()

    print(
        f"{threading.current_thread().name} "
        f"started delay = {delay}"
    )

    url = f"http://localhost:8080/delay/{delay}"

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
    delays = [6,3,1,0,4,5,2]

    async with httpx.AsyncClient(timeout = 10) as client:
        # Calling an async function creates coroutine objects, which are
        # already awaitable. However, they are not independently scheduled
        # just by being created
        coroutines = [fetch(client, delay) for delay in delays]
        # gather() accepts the coroutine objects, schedules them to run
        # concurrently, waits for all of them to finish, and returns their
        # results in the same order the awaitables were passed in
        #
        # Completion order may be roughly 0, 1, 2, 3, 4, 5, 6, but result
        # order is still 6, 3, 1, 0, 4, 5, 2
        results = await asyncio.gather(*coroutines)
        # asyncio.gather() is defined to accept multiple awaitables as
        # separate positional args, not one list argument. Hence, the
        # list of coroutines above needs to be unpacked

    print(results)
    total = time.perf_counter() - start
    print(f"Script total run time: {total:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(main())