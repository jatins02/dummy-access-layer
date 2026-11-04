"""
Step 5: plain code (never the LLM) builds the transaction, hashes and previews it.
"""

import json
from decimal import Decimal
from eth_utils import keccak        # eth uses keccak-256 natively

CHAIN_ID = 31337  # prevents cross-chain replay, Anvil's default
# below is the exact algo used to get eth addresses, transaction hashes and signatures.

def build_transfer(to: str, amount_eth: Decimal, nonce: int) -> dict:
    return {"type": 2, "chainId": CHAIN_ID, "to": to, "value": int(amount_eth * Decimal(10**18)),
            "data": "0x", "nonce": nonce, "gas": 21000,
            "maxFeePerGas": 2_000_000_000, "maxPriorityFeePerGas": 1_000_000_000}


def action_hash(tx: dict) -> str:
    canon = json.dumps(tx, sort_keys=True, separators=(",", ":")).encode()
    return "0x" + keccak(canon).hex()


def preview(tx: dict, alias: str = None) -> str:
    """Generated from the real transaction fields, not from model text."""
    who = f" ({alias})" if alias else ""
    return (f"SEND {Decimal(tx['value']) / Decimal(10**18)} ETH\n"
            f"  to      {tx['to']}{who}\n"
            f"  chain   {tx['chainId']}   nonce {tx['nonce']}   data {tx['data']}\n"
            f"  hash    {action_hash(tx)[:18]}...")
