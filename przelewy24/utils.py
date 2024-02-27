import json
import hashlib


def get_sha384_hash(data: dict) -> str:
    json_str = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    message_bytes = json_str.encode("utf-8")
    sha384_hash = hashlib.sha384(message_bytes)
    return sha384_hash.hexdigest()
