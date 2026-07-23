import secrets
import string

ALPHABET = string.ascii_lowercase + string.digits
LENGTH = 8


def generate() -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(LENGTH))
