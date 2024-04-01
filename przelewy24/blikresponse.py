from typing import Optional

from dataclasses import dataclass, asdict


@dataclass
class BLIKResponse:
    success: bool
    message: str
    error_code: Optional[int] = None
    order_id: Optional[int] = None

    def to_dict(self):
        return {
            "success": self.success,
            "message": self.message,
            "error_code": self.error_code,
            "order_id": self.order_id,
        }
