import asyncio
import websockets

async def echo(websocket, path):
    # 处理接收到的消息
    async for message in websocket:
        print(f"Received message: {message}")

# 启动 WebSocket 服务器，监听 localhost 的 8765 端口
start_server = websockets.serve(echo, "localhost", 8765)

# 运行异步事件循环
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()