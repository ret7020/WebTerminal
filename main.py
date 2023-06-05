from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn
import time
import subprocess

app = FastAPI(title="Web Terminal", version="0.0.1")

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <div id='messages'>
        </div>
        <script>
            var ws = new WebSocket("ws://localhost:8080/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('div')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/", tags=['status'])
async def health_check():
    return {
        "name": app.title,
        "version": app.version
    }


@app.get("/ui")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def shell(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        proc = subprocess.Popen(['ping','ya.ru', '-c', '3'],stdout=subprocess.PIPE)
        for line in iter(proc.stdout.readline,''):
            if not line:
                break
            await websocket.send_text(f"{line.rstrip()}")
            

        
            

if __name__ == "__main__":
    uvicorn.run("main:app", port=8080, host="0.0.0.0", reload=True)
