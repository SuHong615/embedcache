# embedcache

A tiny, dependency-free SQLite cache for text embeddings. Avoid re-calling your
embedding provider for the same text twice, with optional time-to-live expiry.

## Features

- Zero dependencies (Python standard library only).
- Persistent storage in a single SQLite file with WAL mode.
- Optional TTL: entries older than `ttl` seconds are reported as expired.
- Context-manager support (`with EmbeddingCache(...) as cache:`).

## Install

```bash
pip install -e .
```

## Quick start

```python
from embedcache import EmbeddingCache

with EmbeddingCache("cache.db", ttl=3600) as cache:
    cache.set("hello world", [0.01, 0.02, 0.03])
    vector = cache.get("hello world")
    print(vector)  # [0.01, 0.02, 0.03]
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT