"""
Step 7: the signer. The key exists ONLY here. It re-checks everything itself.
"""

from eth_account import Account

from . import approval
from .txbuilder import CHAIN_ID


class SignerRefused(Exception):     # Refusal error to distinguish from bugs
    pass


class Signer:
    def __init__(self, approval_secret: bytes, max_value_wei: int = 10**17):
        self._acct = Account.create()          # synthetic test key (loaded from OS/hardware) - read more about this
        self._secret = approval_secret         # shared hmac secret
        self._used = set()                     # IDs of already-consumed approvals, replay protection (what is the threat, read more).
        self._max = max_value_wei              # hard ceiling, independent of policy

    @property
    def address(self) -> str:
        return self._acct.address

    # ap, the approval ticket dict (from step 6) {hash, expiry, id, mac}
    def sign(self, tx: dict, ap: dict) -> dict:
        if tx["chainId"] != CHAIN_ID:
            raise SignerRefused("wrong chain")
        if tx["data"] != "0x":
            raise SignerRefused("only plain transfers are supported")
        if tx["value"] > self._max:
            raise SignerRefused("above signer hard ceiling")
        try:
            approval.verify(self._secret, tx, ap, self._used)
        except ValueError as e:
            raise SignerRefused(str(e))
        # if successful tx
        self._used.add(ap["id"])
        signed = self._acct.sign_transaction(tx)
        raw = getattr(signed, "raw_transaction", None) or signed.rawTransaction
        return {"tx_hash": "0x" + signed.hash.hex().removeprefix("0x"), "raw": raw.hex()}
