import httpx
import json

cmd = input(">")
url = 'http://127.0.0.1:8080'
header = None
try:
    with httpx.stream('POST', f"{url}/exec", json={"command": cmd}) as r:
        for chunk in r.iter_raw():
            line = chunk.decode("utf-8")
            if header is None:
                header = json.loads(line)
            print(line, end="")

except KeyboardInterrupt:
    httpx.request('GET', f"{url}/kill?pid={header['pid']}")
    print("Stop process")
