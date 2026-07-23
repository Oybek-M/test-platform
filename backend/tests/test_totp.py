from app.services.totp import current_code, new_secret, verify_code


def test_new_secret_is_nonempty_string():
    secret = new_secret()
    assert isinstance(secret, str)
    assert len(secret) > 0


def test_current_code_then_verify_succeeds_default_6_30():
    secret = new_secret()
    code, seconds_left = current_code(secret)
    assert len(code) == 6
    assert 0 < seconds_left <= 30
    assert verify_code(secret, code) is True


def test_current_code_4_digits():
    secret = new_secret()
    code, _ = current_code(secret, digits=4, period=30)
    assert len(code) == 4
    assert verify_code(secret, code, digits=4, period=30) is True


def test_current_code_period_60():
    secret = new_secret()
    code, seconds_left = current_code(secret, digits=6, period=60)
    assert 0 < seconds_left <= 60
    assert verify_code(secret, code, digits=6, period=60) is True


def test_verify_wrong_code_fails():
    secret = new_secret()
    other_secret = new_secret()
    code, _ = current_code(secret)
    other_code, _ = current_code(other_secret)
    assert other_code != code
    assert verify_code(secret, other_code) is False


def test_verify_garbage_code_fails():
    secret = new_secret()
    assert verify_code(secret, "abcdef") is False
