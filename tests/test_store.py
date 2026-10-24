import time

import pytest

from embedcache import TTL_EXPIRED, EmbeddingCache


@pytest.fixture
def cache(tmp_path):
    with EmbeddingCache(tmp_path / "cache.db") as c:
        yield c


def test_set_and_get_roundtrip(cache):
    cache.set("hello world", [0.1, 0.2, 0.3])
    assert cache.get("hello world") == [0.1, 0.2, 0.3]


def test_get_missing_returns_none(cache):
    assert cache.get("missing") is None


def test_contains(cache):
    cache.set("abc", [1.0])
    assert cache.contains("abc")
    assert not cache.contains("zzz")


def test_overwrite_updates_vector(cache):
    cache.set("abc", [1.0])
    cache.set("abc", [2.0, 3.0])
    assert cache.get("abc") == [2.0, 3.0]
    assert len(cache) == 1


def test_ttl_expiry(cache, tmp_path):
    cache.close()
    with EmbeddingCache(tmp_path / "cache.db", ttl=0.0) as short:
        short.set("abc", [1.0])
        time.sleep(0.01)
        assert short.get("abc") is TTL_EXPIRED


def test_delete_and_clear(cache):
    cache.set("a", [1.0])
    cache.set("b", [2.0])
    cache.delete("a")
    assert cache.get("a") is None
    cache.clear()
    assert len(cache) == 0