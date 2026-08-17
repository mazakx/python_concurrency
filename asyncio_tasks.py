
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
    # Unordered delays make the three different orders visible:
    # creation order follows this list, completion order is roughly shortest
    # delay first, while result-consumption order still follows the task list.
    delays = [6,3,1,0,4,5,2]
    tasks = []
    output = []

    async with httpx.AsyncClient(timeout = 10) as client:
        # create_task() schedules each coroutine, but this loop contains no 
        # await, so main() does not yield control to the event loop until
        # the loop finishes.
        for delay in delays:
            tasks.append(asyncio.create_task(fetch(client, delay)))
        
        # Three different orders matter:
        # 1. creation order:        6, 3, 1, 0, 4, 5, 2
        # 2. completion order:      roughly 0, 1, 2, 3, 4, 5, 6
        # 3. result-consumption order: 6, 3, 1, 0, 4, 5, 2
        #
        # We await tasks by iterating over the original tasks list, so the 
        # output preserves creation order even though the tasks complete 
        # in a different order.
        for task in tasks:
            result = await task
            output.append(result)

    print(output)
    total = time.perf_counter() - start
    print(f"Script total run time: {total:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(main())