from fastapi import FastAPI, WebSocket, HTTPException, status
from fastapi.responses import StreamingResponse
import uvicorn
import time
import subprocess
from pydantic import BaseModel
import json
import signal
import os


class CommandExecIn(BaseModel):
    command: str


app = FastAPI(title="Web Terminal", version="0.0.1")


class Shell:
    def __init__(self) -> None:
        self.pids = []

    def executor(self, data):
        proc = subprocess.Popen(data.split(), stdout=subprocess.PIPE)
        self.pids.append(proc.pid)
        yield json.dumps({"pid": proc.pid}) + "\n"
        for line in iter(proc.stdout.readline, ''):
            if not line:
                break
            yield line


app.shell = Shell()


@app.get("/", tags=['status'])
async def health_check():
    return {
        "name": app.title,
        "version": app.version
    }


@app.websocket("/ws")
async def shell(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        try:
            proc = subprocess.Popen(data.split(), stdout=subprocess.PIPE)
            for line in iter(proc.stdout.readline, ''):
                if not line:
                    break
                await websocket.send_text(f"{line.rstrip()}")
        except Exception as e:
            await websocket.send_text(f"Error: {e}")


@app.get("/processes")
async def get_active_processes():
    return app.shell.pids


@app.get("/kill")
async def kill_process(pid: int):
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No process with such id")


@app.post("/exec")
async def stream(command: CommandExecIn):
    return StreamingResponse(app.shell.executor(command.command), media_type='text/event-stream')


if __name__ == "__main__":
    uvicorn.run("main:app", port=8080, host="0.0.0.0", reload=True)
