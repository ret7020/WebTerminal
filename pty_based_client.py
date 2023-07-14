import pty
import os

output_bytes = []


def read(fd):
    with open("log.txt", "a") as file:
        file.write("Callback\n")
    data = os.read(fd, 1024)
    output_bytes.append(data)
    return data


try:
    pty.spawn(["htop"], read)
    output = str(output_bytes)
except KeyboardInterrupt:
    print(output_bytes)
