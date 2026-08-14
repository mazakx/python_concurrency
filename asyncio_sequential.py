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
    delays = [0,1,2,3,4,5,6]
    output = []
    # httpx.AsyncClient() has a default timeout value of 5 seconds. Since one 
    # of our requests waits for 6 seconds, it raises a ReadTimeout. So we 
    # increase the client timeout to 10 seconds so all requests can complete.
    async with httpx.AsyncClient(timeout = 10) as client:
        for delay in delays:
            result = await fetch(client, delay)
            output.append(result)

    print(output)
    total = time.perf_counter() - start
    print(f"Script total run time: {total:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(main())