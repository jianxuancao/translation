import asyncio
import websockets


async def connect_to_server(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            await websocket.send("Hello WebSocket Server!")


# 要连接的WebSocket服务器的URI
uri = "ws://localhost:8765"

# 运行异步事件循环，连接到服务器
asyncio.get_event_loop().run_until_complete(connect_to_server(uri))
asyncio.get_event_loop().run_forever()
