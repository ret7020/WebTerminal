from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import StreamingResponse, HTMLResponse
import uvicorn
import subprocess
from pydantic import BaseModel
import json
import os
from fastapi.templating import Jinja2Templates
from config import SHELL, HOME
import pty


class CommandExecIn(BaseModel):
    command: str


app = FastAPI(title="Web Terminal", version="0.0.1")
templates = Jinja2Templates(directory="templates")

class Shell:
    def __init__(self) -> None:
        self.pids = {}
        self.home = HOME
        self.path = self.home

    def executor(self, data):
        cmd = [SHELL, "-c", data]

        if "cd" in cmd[2]:
            path = cmd[2].replace("cd", "", 1).strip()
            if not path:  # If only cd command without any args
                self.path = self.home
            elif path.startswith(".."):  # TODO; go upper by tree
                self.path = "/"
            else:  # TODO detect absolute and relative path
                if path[0] == "/":  # absolute path
                    self.path = path
                else:
                    self.path = os.path.join(self.path, path) # Concat sub path to current path
                    print(os.path.join(self.path, path))
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.path)
        self.pids[proc.pid] = proc

        # Send header with running process id
        yield json.dumps({"pid": proc.pid}) + "\n"

        for line in iter(proc.stdout.readline, ''):
            if not line:
                break
            yield line

class PtyShell:
    def __init__(self) -> None:
        pass

    def pty_callback(fd):
        data = os.read(fd, 1024)
        print(data)

    def executor(self, cmd):
        pty.spawn(["htop"], self.pty_callback)



app.shell = Shell()
app.pty_shell = PtyShell() # New WIP shell, will replace general shell later

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/processes")
async def get_active_processes():
    return app.shell.pids


@app.get("/kill")
async def kill_process(pid: int):
    try:
        app.shell.pids[pid].terminate()
        app.shell.pids[pid].wait()
        del app.shell.pids[pid]
    except ProcessLookupError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No process with such id")


@app.post("/exec")
async def exec(command: CommandExecIn):
    return StreamingResponse(app.shell.executor(command.command), media_type='text/event-stream')

@app.post("/exec_pty")
async def exec_pty(command: CommandExecIn):
    return StreamingResponse()

if __name__ == "__main__":
    uvicorn.run("main:app", port=8080, host="0.0.0.0", reload=True)
