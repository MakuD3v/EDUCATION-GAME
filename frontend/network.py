import aiohttp
import json
import asyncio

class NetworkManager:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.ws = None
        self.session = None

    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def login(self, username, password):
        await self.init_session()
        url = f"{self.base_url}/auth/token"
        payload = {"username": username, "password": password}
        async with self.session.post(url, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data["access_token"]
            return None

    async def connect_websocket(self, client_id):
        await self.init_session()
        ws_url = self.base_url.replace("http", "ws") + f"/ws/{client_id}"
        self.ws = await self.session.ws_connect(ws_url)

    async def send(self, message: dict):
        if self.ws:
            await self.ws.send_json(message)

    async def receive(self):
        if self.ws:
            msg = await self.ws.receive()
            if msg.type == aiohttp.WSMsgType.TEXT:
                return json.loads(msg.data)
        return None

    async def close(self):
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()
