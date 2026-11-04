"""
Step 8: wire it together and record a trace (model proposed / user approved / signed / leaked).
"""
from pydantic import ValidationError

from .guard import redact_secrets
from .planner import stub_planner
from .policy import Policy, PolicyViolation
from .schema import Proposal
from .signer import Signer, SignerRefused
from .txbuilder import build_transfer, preview


# possible vulnerabilities with the keyword arguments.
def handle(user_text, *, policy: Policy, signer: Signer, approve_fn, planner=stub_planner,
           doc=None, nonce=0) -> dict:
    
    # trace initialisation
    trace = {"outcome": None, "secret_detected": False, "model_proposed": None, "preview": None,
             "tainted_recipient": False, "approved": False, "signed": None,
             "sent_to_external": ["nothing (local model, local signer)"]}
    
    # redact before the model sees anything.
    clean, trace["secret_detected"] = redact_secrets(user_text)

    try:
        proposal = planner(clean, doc)
    except (ValidationError, ValueError) as e:
        proposal = Proposal(action="clarify", question="I couldn't form a valid request. Rephrase?")
    trace["model_proposed"] = proposal.model_dump(mode="json")

    if proposal.action == "clarify":
        trace["outcome"] = f"clarify: {proposal.question}"
        return trace
    if proposal.action == "balance":
        trace["outcome"] = "balance (simulated): 10 ETH"          # hardcoded
        return trace

    try:
        addr = policy.check(proposal)
    except PolicyViolation as e:
        trace["outcome"] = f"blocked by policy: {e}"
        return trace

    # if all the above 'test' pass
    tx = build_transfer(addr, proposal.amount_eth, nonce)
    trace["tainted_recipient"] = doc is not None and proposal.to.lower() not in user_text.lower()   # injection signal (when the recipient name came from the doc but not from the user prompt)
    trace["preview"] = preview(tx, proposal.to)
    ap = approve_fn(tx, trace["preview"], trace["tainted_recipient"])
    
    if ap is None:
        trace["outcome"] = "declined by user"
        return trace
    trace["approved"] = True
    try:
        trace["signed"] = signer.sign(tx, ap)                         # sign tier
    except SignerRefused as e:
        trace["outcome"] = f"signer refused: {e}"
        return trace
    policy.record(proposal.amount_eth)
    trace["outcome"] = "signed"
    return trace


# ps: doc is the external document that can be supplied (invoice/web/tool) that the model can read - the untrusted input.