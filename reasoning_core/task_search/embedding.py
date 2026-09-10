"""Rank the novelty catalog by meaning rather than by spelling.

`closest_entries` ranks with rapidfuzz, which finds a proposal that reuses a known task's
words under a new name and misses one that describes the same operation in words the
catalog never uses. The second kind is the duplicate the novelty gate exists to catch, and
the critic currently has to find it by reading every catalog line itself.

Configured from the environment the way the reviewer is, so the repo names no vendor:
TASK_SEARCH_EMBED_ENDPOINT, TASK_SEARCH_EMBED_MODEL, TASK_SEARCH_EMBED_KEY_ENV. Unset,
unreachable, or answering in a shape this does not recognise all mean one thing to the
caller -- keep the string ranking you already had. A missing endpoint must cost the gate
its extra ranking and never the run.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

# bge-m3 returns unit-length vectors, so similarity is a plain dot product and there is
# nothing to normalise. Kept as the default because it names a model and not a provider:
# the endpoint and the key still have to come from the environment.
MODEL = "BAAI/bge-m3"
DIMENSIONS = 1024
# The catalog is a few hundred one-line entries -- about 17k tokens in total -- so a wave
# embeds all of it in a handful of requests and there is nothing worth caching on disk.
BATCH = 64
# Same policy as the reviewer's: a rate limit that clears in seconds must not quietly cost
# the gate its ranking. The catalog and the candidates are embedded once per wave, so this
# is a handful of requests, not a per-sample cost.
RETRY_AFTER = (5, 20, 60)
TIMEOUT_SECONDS = 180


def endpoint():
    return os.environ.get("TASK_SEARCH_EMBED_ENDPOINT", "")


def model():
    return os.environ.get("TASK_SEARCH_EMBED_MODEL") or MODEL


def _key():
    name = os.environ.get("TASK_SEARCH_EMBED_KEY_ENV", "")
    return os.environ.get(name, "") if name else ""


def configured():
    """Whether there is an endpoint and a key to reach it with."""
    return bool(endpoint() and _key())


def embed(texts):
    """Unit-length vectors for `texts`, in order.

    Raises rather than returning something shorter or reordered: a caller that silently
    accepted a partial answer would compare a proposal against the wrong catalog entry.
    """
    texts = [str(text) for text in texts]
    if not texts:
        return ()
    url, key, name = endpoint(), _key(), model()
    if not url or not key:
        raise RuntimeError("embedding endpoint is not configured")
    vectors = []
    for start in range(0, len(texts), BATCH):
        vectors.extend(_embed_batch(url, key, name, texts[start:start + BATCH]))
    if len(vectors) != len(texts):
        raise RuntimeError(f"asked for {len(texts)} embeddings, got {len(vectors)}")
    return tuple(vectors)


def _embed_batch(url, key, name, texts):
    request = urllib.request.Request(
        url,
        json.dumps({"model": name, "input": texts}).encode(),
        {"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    rows = _post(request).get("data")
    if not isinstance(rows, list) or len(rows) != len(texts):
        raise RuntimeError("embedding response did not answer every input")
    # Sorted by the index the API reports rather than trusting arrival order, so a
    # provider that answers out of order cannot mislabel a vector with another's text.
    try:
        ordered = sorted(rows, key=lambda row: int(row["index"]))
        return [tuple(float(value) for value in row["embedding"]) for row in ordered]
    except (KeyError, TypeError, ValueError) as error:
        raise RuntimeError(f"embedding response is not in the expected shape: {error}")


def _post(request):
    """POST once, waiting out a rate limit or a server fault the way the reviewer does."""
    for wait in (*RETRY_AFTER, None):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            transient = error.code == 429 or error.code >= 500
            if not transient or wait is None:
                raise RuntimeError(f"embedding request failed: {error}") from error
            time.sleep(wait)
        except OSError as error:
            raise RuntimeError(f"embedding endpoint unreachable: {error}") from error
    raise RuntimeError("embedding request exhausted its retries")


def similarity(left, right):
    """Cosine similarity, which is a dot product because the vectors arrive unit-length."""
    return sum(a * b for a, b in zip(left, right))


def rank(query, vectors, limit):
    """Positions of the `limit` vectors closest to `query`, closest first."""
    scored = sorted(
        range(len(vectors)),
        key=lambda position: (-similarity(query, vectors[position]), position),
    )
    return tuple(scored[:limit])
