import sys
import json
import uuid
import os
import requests
import websocket

BASE_URL = os.environ.get("KAGGLE_KERNEL_PROXY_URL")
KERNEL_ID = "aeff28e4-2346-49bd-a934-3994b2a97292"


def run_remote(code: str, timeout: int = 300):
    if not BASE_URL:
        raise RuntimeError(
            "Set KAGGLE_KERNEL_PROXY_URL to the Kaggle kernel proxy URL before running."
        )
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
                print(
                    "\n".join(res["content"].get("traceback", [])),
                    file=sys.stderr,
                    flush=True,
                )
            elif mtype == "execute_reply":
                break
    ws.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            run_remote(f.read())
    else:
        run_remote(sys.stdin.read())
