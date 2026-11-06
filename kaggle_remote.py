import sys
import json
import uuid
import requests
import websocket

BASE_URL = "https://kkb-production.jupyter-proxy.kaggle.net/k/365630327/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwidHlwIjoiSldUIn0..RnN2r8um1vYdqoIWXP5HWA.ufQre4lt_wA6Jbttk-0NrkmAC2kr8uda-4AczFfynCR_ClvOASRKNn24WxyyJPNCCNCwQ_9_J19_YMQ7DoBt62g5aPq9Ctg2lsBD9lWmxm4sd0N191ZjMx9a3qLVWtCAqaV-B_pQEMOuVdvlVe6ffez36Jg2_CD3xPT8AM8WcwzhxHfGDhs8wojT91EfUGcAGpT5HdyTZVdPjRC_LGbZm9L3IY0KvQSbpl3kR_94KS2gVTgzByWBwzv9yjlhpac-.6YkUuoGiKK9P-fGeIH3N3Q/proxy"
KERNEL_ID = "aeff28e4-2346-49bd-a934-3994b2a97292"

def run_remote(code: str, timeout: int = 300):
    ws_url = BASE_URL.replace("https://", "wss://") + f"/api/kernels/{KERNEL_ID}/channels"
    ws = websocket.create_connection(ws_url, timeout=timeout)
    msg_id = str(uuid.uuid4())
    msg = {
        "header": {
            "msg_id": msg_id,
            "username": "kaggle",
            "session": str(uuid.uuid4()),
            "msg_type": "execute_request",
            "version": "5.3",
        },
        "parent_header": {},
        "metadata": {},
        "content": {
            "code": code,
            "silent": False,
            "store_history": True,
            "user_expressions": {},
            "allow_stdin": False,
        },
    }
    ws.send(json.dumps(msg))
    while True:
        res = json.loads(ws.recv())
        if res.get("parent_header", {}).get("msg_id") == msg_id:
            mtype = res["header"]["msg_type"]
            if mtype == "stream":
                print(res["content"]["text"], end="", flush=True)
            elif mtype in ("execute_result", "display_data"):
                data = res["content"].get("data", {})
                if "text/plain" in data:
                    print(data["text/plain"], flush=True)
            elif mtype == "error":
                print("\n".join(res["content"].get("traceback", [])), file=sys.stderr, flush=True)
            elif mtype == "execute_reply":
                break
    ws.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            run_remote(f.read())
    else:
        run_remote(sys.stdin.read())
