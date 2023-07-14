import pty
import os

output_str = ""


def read(fd):
    global output_str
    data = os.read(fd, 1024)
    # output_str += data.decode("utf-8")
    with open("log.txt", "a") as fd:
        fd.write(f"{data.decode('utf-8')}")
    return data


pty.spawn(["/bin/bash", "-c", "ls -lh"], read)
# print("Process finished")