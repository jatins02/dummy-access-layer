"""
Step 6: bind the user's 'yes' to one transaction hash, once, for a short time.
Dummy version uses an HMAC shared between approval UI and signer. A real build would use
a user-presence signature (hardware key / OS prompt) instead of a shared secret.
"""

import hashlib
import hmac
import secrets
import time
from .txbuilder import action_hash

# outputs a fixed length (64) hash
def _mac(secret: bytes, h: str, expiry: int, nid: str) -> str:
    return hmac.new(secret, f"{h}|{expiry}|{nid}".encode(), hashlib.sha256).hexdigest()

# action_hash uses canonical hash, so canonicalisation attack can be used.
def issue(secret: bytes, tx: dict, ttl: int = 60) -> dict:
    h, exp, nid = action_hash(tx), int(time.time()) + ttl, secrets.token_hex(8)
    return {"hash": h, "expiry": exp, "id": nid, "mac": _mac(secret, h, exp, nid)}

# during all this the secret has to be kept secret some other way, because we are passing it as is to these functions (possibly another vulnerablitity).
def verify(secret: bytes, tx: dict, ap: dict, used: set) -> None:
    if not hmac.compare_digest(ap["mac"], _mac(secret, ap["hash"], ap["expiry"], ap["id"])):
        raise ValueError("bad approval MAC")
    if ap["hash"] != action_hash(tx):
        raise ValueError("transaction differs from what was approved")
    if time.time() > ap["expiry"]:
        raise ValueError("approval expired")
    if ap["id"] in used:
        raise ValueError("approval already used")


