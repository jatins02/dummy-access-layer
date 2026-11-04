# Dummy access layer

A tiny, runnable model of the PS architecture. No chain and no LLM needed: signing is real
(eth-account), the planner is a rule-based stub, Ollama to be plugged in later.

    pip install -r requirements.txt
    python -m pytest -q        # 17 attack tests
    python cli.py              # interactive demo

Pipeline: guard -> planner -> schema -> policy -> tx builder -> preview -> approval -> signer

| File | Role | PS requirement it demonstrates |
|---|---|---|
| dal/guard.py | redact keys and seed phrases | protects private information |
| dal/planner.py | the "model" (stub / Ollama) | understands the request, asks to clarify |
| dal/schema.py | closed action vocabulary | model outputs are checked before use |
| dal/policy.py | allowlist and limits | respects permission |
| dal/txbuilder.py | builds tx and hash, makes preview | signed == what user saw |
| dal/approval.py | binds consent to one hash | user stays in control |
| dal/signer.py | only holder of the key | no unchecked signing |
| tests/test_attacks.py | attacks | resistance to attacks |

Known simplifications (honest limits): signer runs in-process; approval uses a shared HMAC
secret; seed detection is a heuristic; the stub planner is not an LLM; amounts are ETH only.
