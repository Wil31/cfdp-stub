import asyncio, websockets, json

URI = "ws://localhost:8000/ws"

async def main():
    async with websockets.connect(URI) as ws:
        print("B:", await ws.recv())

        # reste en écoute
        while True:
            msg = await ws.recv()
            print("B:", msg)

asyncio.run(main())
