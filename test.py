# import selectors
# import subprocess
# import sys

# p = subprocess.Popen(
#     ["ping", "ya.ru"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
# )

# sel = selectors.DefaultSelector()
# sel.register(p.stdout, selectors.EVENT_READ)
# sel.register(p.stderr, selectors.EVENT_READ)

# while True:
#     for key, _ in sel.select():
#         data = key.fileobj.read1().decode()
#         if not data:
#             exit()
#         if key.fileobj is p.stdout:
#             print("Ok:", data, end="")
#             # p.terminate()
#         else:
#             print("Err:", data, end="", file=sys.stderr)

import pty, os

output_bytes = []

def read(fd):
    data = os.read(fd, 1024)
    output_bytes.append(data)
    return data

try:
    pty.spawn(["hashcat", "-b"], read)
    output = str(output_bytes)
except KeyboardInterrupt:
    print(output_bytes)
# parse output as you need