from typing import Any, Iterable

class Optimizer:
    def optimize(self, candidates: Iterable[Any]) -> Any:
        # naive optimizer: return first
        return next(iter(candidates), None)
