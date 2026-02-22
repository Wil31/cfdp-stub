import asyncio, websockets, json

URI = "ws://localhost:8000/ws"

async def main():
    ws = await websockets.connect(URI)
    try:
        # message de bienvenu
        print("A:", await ws.recv())
        # envoi de setAckProb à 0.5
        await ws.send(json.dumps({"type":"command","action":"setAckProb","value":0.4}))
        # reponse a la commande 
        print("A:", await ws.recv())

        # envoi d'un paquet pour voir un ACK/NAK avec nouvelle proba
        await ws.send(json.dumps({"id":"A-1","payload":"hello"}))
        print("A:", await ws.recv())

        await asyncio.sleep(10)
    finally:
        try:
            await asyncio.wait_for(ws.close(), timeout=2)
        except asyncio.TimeoutError:
            print("Timeout lors de la fermeture du WebSocket")

asyncio.run(main())