from dataclasses import dataclass, asdict


@dataclass
class OfflineResponse:
    order_id: int
    session_id: str
    amount: int
    statement: str
    iban: str
    iban_owner: str
    iban_owner_address: str

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "session_id": self.session_id,
            "amount": self.amount,
            "statement": self.statement,
            "iban": self.iban,
            "iban_owner": self.iban_owner,
            "iban_owner_address": self.iban_owner_address,
        }
