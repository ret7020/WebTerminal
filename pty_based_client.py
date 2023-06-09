import pty
import os

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
