from typing import Any

class Storage:
    def __init__(self, base_path: str | None = None):
        self.base_path = base_path or "."

    def save(self, key: str, data: Any) -> str:
        # naive save stub
        path = f"{self.base_path}/{key}"
        with open(path, "w") as f:
            f.write(str(data))
        return path

    def load(self, key: str) -> str:
        path = f"{self.base_path}/{key}"
        with open(path, "r") as f:
            return f.read()
