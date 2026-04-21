from typing import Any
import json


def parse_list_str(v: Any) -> list[str]:
    if isinstance(v, str):
        if not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        return json.loads(v)

    elif isinstance(v, list):
        return [str(i).strip() for i in v]

    raise ValueError(f"Formato inválido: {v}")

def parse_max_size(v: Any) -> int:
    if isinstance(v, int):
        if v <= 0:
            raise ValueError("MAX_SIZE deve ser positivo")
        return v

    if isinstance(v, str):
        v = v.strip().upper()

        if v.endswith("MB"):
            return int(v.replace("MB", "").strip()) * 1024 * 1024
        if v.endswith("KB"):
            return int(v.replace("KB", "").strip()) * 1024
        if v.isdigit():
            return int(v)

    raise ValueError(f"Formato inválido para MAX_SIZE: {v}")
