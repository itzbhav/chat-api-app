from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, Response
import redis.asyncio as aioredis
import asyncio
import json
import os
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="Real-Time Chat API")

message_counter = Counter(
    'chat_messages_total',
    'Total number of chat messages sent',
    ['room']
)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# ---------- Health ----------
@app.get("/health")
async def health():
    return {"status": "ok"}

# ---------- Prometheus Metrics ----------
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# ---------- Send Message (REST) ----------
@app.post("/send")
async def send_message(room: str, username: str, message: str):
    r = aioredis.from_url(REDIS_URL)
    payload = json.dumps({"username": username, "message": message, "room": room})
    await r.publish(f"room:{room}", payload)
    await r.lpush(f"history:{room}", payload)
    await r.ltrim(f"history:{room}", 0, 49)   # keep last 50 messages
    await r.aclose()
    message_counter.labels(room=room).inc()
    return {"status": "sent", "room": room, "username": username, "message": message}

# ---------- Message History (REST) ----------
@app.get("/history/{room}")
async def get_history(room: str):
    r = aioredis.from_url(REDIS_URL)
    raw = await r.lrange(f"history:{room}", 0, 49)
    await r.aclose()
    messages = [json.loads(m) for m in raw]
    return {"room": room, "messages": messages}

# ---------- WebSocket Live Chat ----------
@app.websocket("/chat/{room}")
async def websocket_chat(websocket: WebSocket, room: str):
    await websocket.accept()
    r = aioredis.from_url(REDIS_URL)
    pubsub = r.pubsub()
    await pubsub.subscribe(f"room:{room}")
    try:
        async def listener():
            async for msg in pubsub.listen():
                if msg["type"] == "message":
                    await websocket.send_text(msg["data"].decode())
        listen_task = asyncio.create_task(listener())
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            payload["room"] = room
            await r.publish(f"room:{room}", json.dumps(payload))
            await r.lpush(f"history:{room}", json.dumps(payload))
            await r.ltrim(f"history:{room}", 0, 49)
    except WebSocketDisconnect:
        listen_task.cancel()
    finally:
        await pubsub.unsubscribe(f"room:{room}")
        await r.aclose()
