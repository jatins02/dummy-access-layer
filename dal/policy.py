"""
Step 4: policy engine. Deterministic code that decides what the user allows.
"""
from decimal import Decimal


# exact error, so policy refusals can be distinguished from bugs
class PolicyViolation(Exception):
    pass


# class raises an error, in case of any discrepancy, otherwise records tx and passes on.
class Policy:
    def __init__(self, contacts, per_tx_limit="0.05", daily_limit="0.1"):
        self.contacts = {k.lower(): v for k, v in contacts.items()}     # keys lowercased, so lookups are case-insensitive. this is the allowlist.
        self.per_tx = Decimal(per_tx_limit)     # max eth per single transaction
        self.daily = Decimal(daily_limit)       # max eth per day
        self.spent_today = Decimal(0)           # running total for the daily limit

    # p is for Proposal
    def check(self, p):
        if p.action != "send":
            return None
        addr = self.contacts.get(p.to.lower())
        if addr is None:
            raise PolicyViolation(f"recipient '{p.to}' is not in your contacts")
        if p.amount_eth > self.per_tx:
            raise PolicyViolation(f"{p.amount_eth} ETH exceeds per-transaction limit {self.per_tx}")
        if self.spent_today + p.amount_eth > self.daily:
            raise PolicyViolation(f"would exceed daily limit {self.daily} (spent {self.spent_today})")
        # standardised (lowercased, more standardisation in the username - eth docs) addr returned, if valid spending.
        return addr

    def record(self, amount):
        self.spent_today += amount
