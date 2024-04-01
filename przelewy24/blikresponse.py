from dataclasses import dataclass
from typing import Optional, Dict, Union


@dataclass
class BLIKResponse:
    success: bool
    message: str
    error_code: Optional[int] = None
    order_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Union[bool, str, int, None]]:
        return {
            "success": self.success,
            "message": self.message,
            "error_code": self.error_code,
            "order_id": self.order_id,
        }
