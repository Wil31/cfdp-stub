
import random
from app.config import settings

REQUIRED_FIELDS = {"id", "payload"}

ACK_COUNT = 0
NAK_COUNT = 0

def validate(packet: dict) -> tuple[bool, str | None]:
    missing = REQUIRED_FIELDS - set(packet)
    if missing:
        return False, f"Champs manquants: {', '.join(sorted(missing))}"
    return True, None

def set_ack_probability(p: float) -> None:
    settings.ACK_PROBABILITY = p

def ack_or_nak() -> str:
    global ACK_COUNT, NAK_COUNT
    res = "ACK" if random.random() < settings.ACK_PROBABILITY else "NAK"
    if res == "ACK":
        ACK_COUNT += 1
    else:
        NAK_COUNT += 1
    return

def process_packet(packet: dict) -> dict:
    ok, err = validate(packet)
    if not ok:
        return {"status": "NAK", "error": err}
    return {"status": ack_or_nak(), "id": packet["id"]}


def ws_process(message: dict) -> dict:
    ok, err = validate(message)
    if not ok:
        return {"type": "response", "status": "NAK", "error": err}
    return {"type": "response", "status": ack_or_nak(), "id": message["id"]}
