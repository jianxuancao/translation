import asyncio
import websockets

async def echo(websocket):
    async for message in websocket:
        print(f"Server 8888 received: {message}")
        # echo to confirm
        await websocket.send(message)

start_server_8888 = websockets.serve(echo, "localhost", 8887)

asyncio.get_event_loop().run_until_complete(start_server_8888)
asyncio.get_event_loop().run_forever()