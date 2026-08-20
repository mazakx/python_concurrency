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
    delays = [6, 3, 1, 0, 4, 5, 2]
    results = []

    async with httpx.AsyncClient(timeout=10) as client:

        # Calling an async function creates coroutine objects, which are
        # awaitable but are not independently scheduled just by being created.
        coroutines = [fetch(client, delay) for delay in delays]

        # as_completed() accepts an iterable of awaitables. This can be raw
        # coroutine objects, as here, or Task objects created explicitly with
        # create_task().
        #
        # When raw coroutines are supplied, as_completed() schedules them so
        # they can run concurrently. Explicit create_task() is only needed
        # when we want direct control over individual Tasks, such as cancelling,
        # inspecting, naming, storing, or awaiting a specific Task elsewhere.
        #
        # Unlike gather(), as_completed() exposes results in completion order
        # rather than preserving submission order. Each returned awaitable is
        # awaited to retrieve the result of whichever operation completed next.
        #
        # When raw coroutine objects are passed to as_completed(), their initial
        # execution order is not guaranteed to match the order of the input iterable.
        # Only completion-order exposure is the behavior we should rely on.
        for completed_task in asyncio.as_completed(coroutines):
            result = await completed_task
            results.append(result)

    print(results)
    total = time.perf_counter() - start
    print(f"Script total run time: {total:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(main())