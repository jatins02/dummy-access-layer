"""Interactive demo:  python cli.py   (type 'quit' to exit)"""
import json
import secrets

from dal import approval
from dal.pipeline import handle
from dal.planner import stub_planner
from dal.policy import Policy
from dal.signer import Signer

ALICE = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
BOB = "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"
SECRET = secrets.token_bytes(32)
signer = Signer(SECRET)
policy = Policy({"alice": ALICE, "bob": BOB})
print(f"Test wallet: {signer.address}  |  contacts: alice, bob  |  limits 0.05/tx, 0.1/day")


def ask_user(tx, preview, tainted):
    print("\n--- APPROVAL REQUIRED ---\n" + preview)
    if tainted:
        print("  WARNING: recipient came from external content, not from you")
    return approval.issue(SECRET, tx) if input("Approve? [y/N] ").lower() == "y" else None


nonce = 0
while (text := input("\nyou> ")) != "quit":
    t = handle(text, policy=policy, signer=signer, planner=stub_planner, approve_fn=ask_user, nonce=nonce)
    nonce += t["outcome"] == "signed"
    print(json.dumps(t, indent=2, default=str))
