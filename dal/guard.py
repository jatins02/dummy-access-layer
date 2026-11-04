"""
Step 2: input guard. Keep keys and seed phrases out of model input and logs.
"""

import re

HEX_KEY = re.compile(r"\b(0x)?[0-9a-fA-F]{64}\b")
# Heuristic only: 12+ consecutive short lowercase words. Real version: use the BIP-39 wordlist.
SEED_LIKE = re.compile(r"(?:\b[a-z]{3,8}\b[ ,]+){11,}\b[a-z]{3,8}\b")


def redact_secrets(text: str):
    flagged = False
    for pat in (HEX_KEY, SEED_LIKE):
        if pat.search(text):
            flagged = True
            text = pat.sub("[REDACTED-SECRET]", text)
    return text, flagged

