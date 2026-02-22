
from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.responses import JSONResponse
from app.config import settings
from app.cfdp_stub import process_packet, ws_process, set_ack_probability, ACK_COUNT, NAK_COUNT
from app.models import Packet
from typing import Set
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(title=settings.APP_NAME)

# In-memory store pour l'entraînement
STORE: dict[str, dict] = {}

@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, 
            "ack_probability": settings.ACK_PROBABILITY}

@app.get("/stats")
def stats():
    return {"acks": ACK_COUNT, "naks": NAK_COUNT}

@app.post("/packets")
def receive_packet(packet: Packet):
    result = process_packet(packet.model_dump())
    STORE[packet.id] = packet.model_dump()
    return JSONResponse(result)

@app.get("/packets/{packet_id}")
def get_packet(packet_id: str):
    if packet_id not in STORE:
        raise HTTPException(status_code=404, detail="Packet not found")
    return STORE[packet_id]

ACTIVE_CLIENTS: Set[WebSocket] = set()

@app.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    logging.info("WS connected: %s", ws.client)
    ACTIVE_CLIENTS.add(ws)
    try:
        await ws.send_json({"status": "READY", "ack_probability": settings.ACK_PROBABILITY})
        while True:
            try:
                data = await ws.receive_json()
            except WebSocketDisconnect:
                logging.info("WS disconnected: %s", ws.client)
                break
            except Exception as e:
                logging.warning("WS error: %s", e)
                break

            # 1) commandes
            if isinstance(data, dict) and data.get("type") == "command":
                action = data.get("action")
                if action == "setAckProb":
                    #validation
                    value = data.get("value")
                    if value is None:
                        await ws.send_json({"type": "system", "status": "ERROR", "reason": "Value is required"})
                        continue
                    try:
                        val = float(value)
                    except (TypeError, ValueError):
                        await ws.send_json({"type": "system", "status": "ERROR", "reason": "value must be a number"})
                        continue
                    if not (0.0 <= val <= 1.0):
                        await ws.send_json({"type":"system","status":"ERROR","reason":"Value must be between 0.0 and 1.0"})
                        continue
                    set_ack_probability(val)
                    logging.info("ACK probability updated to %.2f by %s", val, ws.client)
                    # reponse à l'émetteur
                    await ws.send_json({"type":"system","status":"OK","ack_probability": val})
                    for client in list(ACTIVE_CLIENTS):
                        if client is not ws:
                            try:
                                await client.send_json({"type":"system","status":"UPDATED","ack_probability":val})
                            except Exception:
                                # client mort: on le retire
                                ACTIVE_CLIENTS.discard(client)
                    continue
                await ws.send_json({"type":"system","status":"ERROR","reason":f"Unknown action '{action}'"})
                continue

            # 2) paquet classique
            resp = ws_process(data)
            await ws.send_json(resp)

    except Exception as e:
        logging.warning("WS error: %s", e)
        pass
    finally:
        ACTIVE_CLIENTS.discard(ws)
        logging.info("WS disconnected: %s", ws.client)
