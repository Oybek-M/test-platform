import time

import pyotp


def new_secret() -> str:
    return pyotp.random_base32()


def _totp(secret: str, digits: int, period: int) -> pyotp.TOTP:
    return pyotp.TOTP(secret, digits=digits, interval=period)


def current_code(secret: str, digits: int = 6, period: int = 30) -> tuple[str, int]:
    t = _totp(secret, digits, period)
    code = t.now()
    seconds_left = period - (int(time.time()) % period)
    return code, seconds_left


def verify_code(secret: str, code: str, digits: int = 6, period: int = 30) -> bool:
    return _totp(secret, digits, period).verify(code, valid_window=1)
