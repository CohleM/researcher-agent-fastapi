from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from websocket_manager import WebSocketManager
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
import time
from typing import AsyncGenerator, NoReturn
from websocket_manager import WebSocketManager

manager = WebSocketManager()

app = FastAPI()
client = AsyncOpenAI()

# with open("index.html") as f:
#     html = f.read()


async def get_ai_response(message: str) -> AsyncGenerator[str, None]:
    """
    OpenAI Response
    """
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant, skilled in explaining "
                    "complex concepts in simple terms."
                ),
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        stream=True,
    )

    all_content = ""
    async for chunk in response:
        content = chunk.choices[0].delta.content
        finish_reason = chunk.choices[0].finish_reason
        # print("haha", content)
        # if content:
        # all_content += content
        if content:
            all_content += content

        yield all_content, finish_reason


# @app.get("/")
# async def web_app() -> HTMLResponse:
#     """
#     Web App
#     """
#     return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> NoReturn:
    """
    Websocket for AI responses
    """

    await manager.connect(websocket)

    while True:
        message = await websocket.receive_text()
        print("message printing from backend", message)
        async for text, finish_reason in get_ai_response(message):
            # print(text, finish_reason)
            await websocket.send_json({"content": text, "finish_reason": finish_reason})


# if __name__ == "__main__":
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         log_level="debug",
#         reload=True,
#     )
