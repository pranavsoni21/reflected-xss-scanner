from typing import List, Optional

class PayloadGenerator:
    def __init__(self, randomize: bool = True, seed: Optional[int] = None):
        ...

    def generate(self, context: str, param: str, limit: int = 3) -> List[str]:
        ...
