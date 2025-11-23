import random
import string
import html


def make_token(prefix='PAY', n=6) -> str:
    return f"{prefix}_{''.join(random.choices(string.ascii_lowercase+string.digits, k=n))}"


def html_unescape(s: str) -> str:
    return html.unescape(s or '')


def short_snippet(s: str, n: int = 300) -> str:
    return (s[:n] + '...') if len(s) > n else s
