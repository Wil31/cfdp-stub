
# Mini projet stub CFDP (REST + WebSocket) 

Un mini‑service Python (FastAPI) qui simule la réception de paquets et renvoie **ACK/NAK**.
Il inclut : Docker, docker‑compose et un **Helm Chart** pour Kubernetes.

## Prérequis
- Python 3.10+
- Docker (facultatif pour l'étape conteneur)
- Helm 3 & un cluster K8s (minikube/kind) pour l'étape Helm (facultatif)

---
## 1) Lancer en local (sans Docker)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
- Healthcheck : http://localhost:8000/health
- Docs OpenAPI : http://localhost:8000/docs
- WebSocket : ws://localhost:8000/ws

### Exemples REST
```bash
# Envoi d'un paquet
curl -X POST http://localhost:8000/packets   -H 'Content-Type: application/json'   -d '{"id":"42","payload":"hello"}'

# Récupération d'un paquet
curl http://localhost:8000/packets/42
```

### Exemple WebSocket (terminal)
```bash
python - <<'PY'
import asyncio, websockets, json
async def main():
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        await ws.send(json.dumps({"id":"1","payload":"ping"}))
        print(await ws.recv())
asyncio.run(main())
PY
```

---
## 2) Lancer avec Docker
```bash
docker build -t cfdp-stub:dev .
docker run --rm -p 8000:8000   -e APP_NAME=cfdp-stub   -e ACK_PROBABILITY=0.8   cfdp-stub:dev
```

## 3) docker-compose (dev rapide)
```bash
docker compose up --build
```

---
## 4) Déployer avec Helm
```bash
helm install cfdp ./helm/cfdp-stub   --set image.repository=cfdp-stub   --set image.tag=dev   --set image.pullPolicy=IfNotPresent

# Vérifier les ressources
kubectl get deploy,svc,po

# Désinstaller
helm uninstall cfdp
```
