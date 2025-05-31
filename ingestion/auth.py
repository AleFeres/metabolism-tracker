from pathlib import Path
import os, time, json, requests
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("WHOOP_CLIENT_ID")
CLIENT_SECRET = os.getenv("WHOOP_CLIENT_SECRET")
TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
TOK_FILE = Path("data/auth/whoop_token.json")

# --- internal helpers -------------------------------------------------------

def _save(tok):
    TOK_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TOK_FILE, "w") as f:
        json.dump(tok, f)

def _load():
    if TOK_FILE.exists():
        return json.load(open(TOK_FILE))
    return None

# --- public API -------------------------------------------------------------

def get_access_token():
    tok = _load() or {}
    if tok and time.time() < tok.get("expires_at", 0):
        return tok["access_token"]

    r = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": os.getenv("WHOOP_REFRESH_TOKEN") or tok.get("refresh_token"),
        },
        auth=(CLIENT_ID, CLIENT_SECRET),
        timeout=30,
    )

    print("WHOOP token raw resp:", r.status_code, r.text)   # ← temporary debug line

    r.raise_for_status()          # crashes early if HTTP ≠ 200
    resp = r.json()
    resp["expires_at"] = time.time() + resp.get("expires_in", 0)

