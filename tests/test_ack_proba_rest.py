import argparse
import json
import random
import time
import statistics
import requests

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--n", type=int, default=1000, help="Nombre de paquets")
    parser.add_argument("--id-prefix", default="R")
    parser.add_argument("--sleep", type=float, default=0.0, help="Pause entre requetes (sec)")
    args = parser.parse_args()

    url_post = f"{args.base_url}/packets"
    url_stats = f"{args.base_url}/stats"

    acks_count = 0
    naks_count = 0

    t0 = time.time()
    for i in range(args.n):
        payload = {"id": f"{args.id_prefix}-{i}", "payload": "hello"}
        r = requests.post(url_post, json=payload, timeout=5)
        r.raise_for_status()
        data = r.json()
        if data.get("status") == "ACK":
            acks_count += 1
        else:
            naks_count += 1
        if args.sleep:
            time.sleep(args.sleep)
    delta_t0 = time.time() - t0

    observed = acks_count / args.n if args.n > 0 else float("nan")

    # recupérer la proba côté serv
    try:
        s = requests.get(url_stats, timeout=3).json()
    except Exception:
        s = {}
    try:
        h= requests.get(f"{args.base_url}/health", timeout=3).json()
        configured = h.get("ack_probability")
    except Exception:
        configured = None

    print(f"total: {args.n} | ACK: {acks_count} | NAK: {naks_count} | ACK%: {observed*100:.2f}% | time : {delta_t0:.2f}s")
    if configured is not None:
        print(f"Configured ACK proba server: {configured:.3f}")
    
    #borne d'intervalle de confiance
    if args.n > 0:
        p = observed
        n= args.n
        # ecart type approx binomial: sqrt(p*(1-p)/n)
        stdev = (p*(1-p)/n) ** 0.5
        print(f"Approx 95% CI pour ACK%: [{(p-1.96*stdev)*100:.2f}%,{(p+1.96*stdev)*100:.2f}%]")

if __name__ == "__main__":
    main()
