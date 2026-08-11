import requests
import time
import threading

def fetch(delay: int) -> str:
    url = f"https://httpbin.org/delay/{delay}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["url"]

def main() -> None:
    start = time.perf_counter()
    delays = [0,1,2,3,4,5,5]
    output = []
    for number,delay in enumerate(delays, start = 1):
        result = fetch(delay)
        elapsed = time.perf_counter() - start
        output.append(result)
        print(f"Starting delay={delay} on {threading.current_thread().name }"
              f"{number} request returned in {elapsed:.4f} seconds ")
    print(output)

    total = time.perf_counter() - start
    print(f"Script total run time: {total:.4f} seconds")



if __name__ == "__main__":
    main()