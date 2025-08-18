import requests
import asyncio
import websockets
import json

API_URL = "https://chess-api.com/v1"
WS_URL = "wss://chess-api.com/v1"
HEADERS = {"Content-Type": "application/json"}

def get_best_move_rest(fen: str, depth: int = None, variants: int = 1) -> dict:
    payload = {"fen": fen}
    if depth: payload["depth"] = depth
    if variants: payload["variants"] = variants
    resp = requests.post(API_URL, json=payload, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()

async def get_best_move_ws(fen: str, variants: int = 1):
    async with websockets.connect(WS_URL) as ws:
        await ws.send(json.dumps({"fen": fen, "variants": variants}))
        async for message in ws:
            data = json.loads(message)
            yield data
            if data.get("type") == "bestmove":
                break

import concurrent.futures
executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


