import pytest
from app.utils.shortener import generate_short_code, is_valid_url


def test_generate_short_code_length():
    code_6 = generate_short_code(6)
    code_8 = generate_short_code(8)
    assert len(code_6) == 6
    assert len(code_8) == 8
    assert code_6 != code_8


def test_generate_short_code_uniqueness():
    codes = {generate_short_code(6) for _ in range(100)}
    assert len(codes) == 100


def test_is_valid_url():
    assert is_valid_url("https://example.com") is True
    assert is_valid_url("http://subdomain.domain.co.uk/path?arg=val#fragment") is True
    assert is_valid_url("ftp://example.com") is False
    assert is_valid_url("not_a_url") is False
    assert is_valid_url("http://") is False
