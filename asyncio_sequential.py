import asyncio
import httpx
import time
import threading

# The async def syntax defines a coroutine function. Calling a coroutine
# function does not run the function, instead it creates a coroutine object
# so calling the below function would return something like: 
# <coroutine object fetch at 0x...>
async def fetch(client: httpx.AsyncClient, delay: int) -> str:
    start = time.perf_counter()

    print(
        f"{threading.current_thread().name} "
        f"started delay = {delay}"
    )

    url = f"http://localhost:8080/delay/{delay}"
    # the await keyword is the heart of the asyncio module, it means: "Start
    # this asynchronous operation" then "if it has to wait, pause this
    # coroutine and give control back to the event loop"
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
    delays = [0,1,2,3,4,5,6]
    output = []

    # httpx.AsyncClient() has a default timeout value of 5 seconds. Since one 
    # of our requests waits for 6 seconds, it raises a ReadTimeout. So we 
    # increase the client timeout to 10 seconds so all requests can complete.

    # We use an async context manager because entering and exiting the client's
    # lifetime may itself involve asynchronous work. For example, when the 
    # client is closed it may need to close open TCP connections and wait for 
    # the peer to acknowledge the shutdown before releasing its resources.
    #
    # A regular context manager implements __enter__() and __exit__() methods, 
    # whereas an async context manager implements __aenter__() and __aexit__(),
    # both of which can suspend execution while waiting for asynchronous
    # operations to complete.
    async with httpx.AsyncClient(timeout = 10) as client:
        for delay in delays:
            result = await fetch(client, delay)
            output.append(result)

    print(output)
    total = time.perf_counter() - start
    print(f"Script total run time: {total:.4f} seconds")

if __name__ == "__main__":
    # The following line does three things:
    # 1. Creates the event loop
    # 2. schedules main()
    # 3. runs the event loop until main() finishes
    asyncio.run(main())