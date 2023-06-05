import selectors
import subprocess
import sys

p = subprocess.Popen(
    ["ping", "ya.ru"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
)

sel = selectors.DefaultSelector()
sel.register(p.stdout, selectors.EVENT_READ)
sel.register(p.stderr, selectors.EVENT_READ)

while True:
    for key, _ in sel.select():
        data = key.fileobj.read1().decode()
        if not data:
            exit()
        if key.fileobj is p.stdout:
            print("Ok:", data, end="")
            # p.terminate()
        else:
            print("Err:", data, end="", file=sys.stderr)
