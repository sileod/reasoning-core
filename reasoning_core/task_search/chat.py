"""Talking to an OpenAI-compatible chat endpoint, and choosing which one to talk to.

Split out of wave_proposer, which had come to own catalog extraction, proposal validation,
prompt construction, HTTP transport, retry policy, key and model routing, critic voting and
orchestration at once. Transport is the part with no opinion about proposals in it: digest,
design_proposer and audit_novelty were all already importing ChatClient from the proposer,
which is the usual sign that an abstraction is in the wrong file.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import re
import sys
import time

import requests


# One 504 from NIM used to end a whole wave. The old backoff was 1s then 2s, which is
# nothing to a provider that needs three minutes to answer at all: retrying that fast
# just asks the same overloaded queue the same question twice and gives up. Wait longer
# than a call takes, and keep waiting -- a wave is hours of work, and losing it to a
# gateway timeout costs far more than sitting out ten minutes.
# Which model to ask, and where, is the caller's decision -- a transport that defaults to
# one names a proposer's preference in a file that should not have one. The key env is the
# exception, kept because callers have always relied on finding one without naming it.
FALLBACK_KEY_ENV = "NVIDIA_API_KEY"
RETRY_STATUS = frozenset({429, 500, 502, 503, 504})
RETRY_BACKOFF = (30, 90, 240, 600)


def _sha256(value):
    if not isinstance(value, bytes):
        value = str(value).encode("utf-8")
    return hashlib.sha256(value).hexdigest()



# Only applied after a genuine parse failure, so a string that happens to contain ", }"
# is never rewritten.
_TRAILING_COMMA = re.compile(r",(\s*[}\]])")


def _loads(text):
    """Parse JSON the way a person would read it back.

    Two things models do that json.loads will not accept, and that cost whole waves. A
    multi-line `rationale` arrives with the break as a raw control character, which
    `strict=False` reads as the character it is. And a list or object closed after a
    trailing comma parses for every human reader; that one is only tried once the real
    parse has already failed. Nothing else about the grammar is relaxed.
    """
    try:
        return json.loads(text, strict=False)
    except json.JSONDecodeError:
        return json.loads(_TRAILING_COMMA.sub(r"\1", text), strict=False)


def _extract_json(text):
    text = str(text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I)
    try:
        return _loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("model response contains no JSON object")
        return _loads(text[start:end + 1])


def provider_of(endpoint):
    """Label a run by where it ran, without a provider registry to keep in sync."""
    host = str(endpoint).split("//", 1)[-1].split("/", 1)[0].split(":", 1)[0]
    parts = [part for part in host.split(".") if part not in {"www", "api"}]
    return ".".join(parts[:-1]) or host


class UpstreamError(RuntimeError):
    """A gateway answered 200 and put the failure in the body.

    OpenRouter reports an upstream 429 or 502 this way, inside a reply that is otherwise
    well-formed HTTP. raise_for_status cannot see it, so without this the retry loop takes
    a failure for an answer and the caller gets a KeyError several frames from the cause.
    """


def _raise_body_error(payload):
    if isinstance(payload, dict) and payload.get("error"):
        error = payload["error"]
        raise UpstreamError(str(error.get("message", error))
                            if isinstance(error, dict) else str(error))


class ChatClient:
    """A JSON-returning OpenAI-compatible chat client.

    Kept deliberately generic: the proposer is worth running wherever the strongest model
    is currently free, and pinning it to one vendor's name was costing a code edit each
    time that changed. `reasoning_effort=None` omits the field, which endpoints that do
    not know it reject the request over.
    """

    def __init__(self, *, model, endpoint, api_key=None, seed=0, temperature=1.0,
                 reasoning_effort="max", timeout=600, stream=True):
        self.model, self.endpoint = model, endpoint
        self.provider = provider_of(endpoint)
        self.api_key = api_key or os.environ.get(FALLBACK_KEY_ENV)
        if not self.api_key:
            raise RuntimeError(f"an API key is required for {self.provider}")
        if reasoning_effort not in {"low", "high", "max", None}:
            raise ValueError("reasoning_effort must be low, high, max or None")
        self.seed, self.temperature = seed, temperature
        self.reasoning_effort, self.timeout = reasoning_effort, timeout
        self.stream = stream
        self.calls = []

    def _poll(self, response, headers):
        payload = response.json()
        request_id = payload.get("requestId")
        if not request_id:
            raise RuntimeError("provider returned 202 without a requestId")
        status_url = self.endpoint.rsplit("/chat/completions", 1)[0] + "/status/" + request_id
        deadline, delay = time.monotonic() + self.timeout, 2
        while time.monotonic() < deadline:
            time.sleep(delay)
            response = requests.get(status_url, headers=headers,
                                    timeout=min(60, self.timeout))
            if response.status_code == 202:
                delay = min(10, delay * 2)
                continue
            response.raise_for_status()
            return response
        raise TimeoutError(f"request {request_id} stayed pending for {self.timeout}s")

    @staticmethod
    def _read_document(response):
        """Content, raw bytes and id from a whole JSON reply."""
        payload = response.json()
        _raise_body_error(payload)
        content = payload["choices"][0]["message"].get("content")
        if isinstance(content, list):
            content = "".join(str(part.get("text", "")) if isinstance(part, dict)
                              else str(part) for part in content)
        return content, response.content, payload.get("id")

    def _read_stream(self, response):
        """Accumulate an SSE reply into the (content, raw bytes, id) a JSON reply gives.

        A proposal batch is minutes of reasoning before the first content token, and NIM's
        gateway closes a request that has sent nothing for long enough: wave9 died on a 504
        at batch 12 and again at batch 6, after exhausting every retry, while a 16-token
        request to the same model answered fine. Streaming is not an optimisation here --
        it is what keeps the connection alive long enough to finish. Measured on kimi-k3
        with the real proposer prompt: first byte at 55s, where the silent request 504s.
        """
        chunks, text, response_id = [], [], None
        for line in response.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue
            payload = line[6:]
            if payload == "[DONE]":
                break
            chunks.append(payload)
            parsed = json.loads(payload)
            _raise_body_error(parsed)
            response_id = response_id or parsed.get("id")
            # reasoning_content is the model thinking aloud, not the answer, and every
            # endpoint that emits it also emits content separately.
            piece = (parsed.get("choices") or [{}])[0].get("delta", {}).get("content")
            if piece:
                text.append(piece)
        return "".join(text), "\n".join(chunks).encode(), response_id

    def _read_reply(self, response, headers):
        """The three ways an endpoint can hand back one answer."""
        if response.status_code == 202:
            # The asynchronous path answers with a whole document however it was asked.
            return self._read_document(self._poll(response, headers))
        return self._read_stream(response) if self.stream else self._read_document(response)

    def json(self, purpose, system, user, max_tokens=32768, wait_out_rate_limits=True):
        """One JSON answer, retrying transport the way a wave needs it.

        `wait_out_rate_limits=False` gives up on a 429 at once instead of climbing the
        ladder. A pool with another key to try wants that: sixteen minutes of backoff to
        learn that this key is exhausted is sixteen minutes the other key could have been
        answering. The last route in a pool still waits, because then there is nothing to
        route to and patience is all that is left.
        """
        body = {
            "model": self.model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "max_tokens": max_tokens,
            "seed": self.seed,
            "temperature": self.temperature,
            "stream": self.stream,
        }
        if self.reasoning_effort:
            body["reasoning_effort"] = self.reasoning_effort
        headers = {"Authorization": "Bearer " + self.api_key,
                   "Accept": "application/json"}
        request_bytes = json.dumps(body, sort_keys=True).encode()
        response_bytes = b""
        for attempt, backoff in enumerate(RETRY_BACKOFF):
            last = attempt == len(RETRY_BACKOFF) - 1
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=body,
                timeout=self.timeout,
                stream=self.stream,
            )
            if response.status_code in RETRY_STATUS:
                # Reading .content here consumes a streamed body, so it happens only on
                # the failures, whose bodies are short and worth keeping for the call log.
                response_bytes = response.content
                if last or (response.status_code == 429 and not wait_out_rate_limits):
                    response.raise_for_status()
                time.sleep(backoff)
                continue
            response.raise_for_status()
            try:
                content, response_bytes, response_id = self._read_reply(response, headers)
            except (UpstreamError, json.JSONDecodeError,
                    requests.RequestException) as failure:
                # Reading the reply is transport, and transport fails transiently. A
                # truncated SSE frame surfaces here as a JSONDecodeError from the chunk
                # parse and used to escape the loop entirely, ending a wave seventeen
                # minutes in on `Unterminated string starting at: line 1 column 125`.
                # A connection dropped mid-stream is the same event wearing another name.
                if last:
                    raise
                response_bytes = str(failure).encode()
                time.sleep(backoff)
                continue
            try:
                result = _extract_json(content)
            except ValueError:
                # A reply that is not JSON is as transient as a 502, and was not treated as
                # one: this parse used to sit outside the loop, so a single malformed object
                # ended a wave that had already cost fifteen minutes. Same prompt, same
                # model, another sample -- which is exactly what a retry is for.
                if last:
                    raise
                response_bytes = str(content).encode()
                time.sleep(backoff)
                continue
            break
        self.calls.append({
            "purpose": purpose,
            # Stamped per call, not per wave: a pool that fell back mid-wave otherwise
            # leaves no way to tell which model wrote which round, which is the one
            # question provenance exists to answer.
            "model": self.model,
            "provider": self.provider,
            "request_sha256": _sha256(request_bytes),
            "response_sha256": _sha256(response_bytes),
            "response_id": response_id,
        })
        return result



class ClientPool:
    """Several clients for one job: preferred model first, keys shared round-robin.

    Two dimensions, because the outage that prompted this had two. NVIDIA's quota is per
    account *and* per model -- one key was refusing kimi-k3 while serving deepseek-v4-pro,
    and a second key was serving both -- so a pool has to be able to step sideways to
    another key and downwards to another model, in that order. Sideways first: a second key
    on the model you asked for beats the first key on a model you did not.

    Consecutive calls start at a rotating offset into each model's keys, so they share
    the load rather than exhausting one key and then discovering the next. A route that
    answers 429 is remembered as closed for `cooldown` seconds: a rotation with no memory
    hands work back to an exhausted key every other call and pays the full retry ladder to
    learn what it was already told.
    """

    def __init__(self, clients, *, cooldown=1800):
        if not clients:
            raise ValueError("a pool needs at least one client")
        # Preference order is the caller's; the rotation only picks where to start within
        # each model's keys, so a pool never prefers a fallback model to a working one.
        self.clients = list(clients)
        self.cooldown = cooldown
        self._closed = {}
        self._turn = itertools.count()
        self._answered = self.clients[0]
        self._log = []

    @property
    def model(self):
        return self._answered.model

    @property
    def provider(self):
        return getattr(self._answered, "provider", None)

    @property
    def calls(self):
        """Answered calls in the order they were answered.

        Concatenating the clients' own logs groups by route instead, which reads as
        though the wave ran each model in turn. A refused route logs nothing, so what is
        recorded here is what actually produced the wave.
        """
        return list(self._log)

    def _routes(self):
        """Every client, preferred model first, starting at a rotating key offset."""
        by_model, order = {}, []
        for client in self.clients:
            if client.model not in by_model:
                by_model[client.model] = []
                order.append(client.model)
            by_model[client.model].append(client)
        start = next(self._turn)
        routes = []
        for model in order:
            group = by_model[model]
            offset = start % len(group)
            routes.extend(group[offset:] + group[:offset])
        return routes

    def _open(self, client):
        until = self._closed.get(id(client))
        return until is None or time.monotonic() >= until

    def json(self, purpose, system, user, **kwargs):
        routes = self._routes()
        live = [client for client in routes if self._open(client)] or routes
        for index, client in enumerate(live):
            try:
                result = client.json(purpose, system, user,
                                     wait_out_rate_limits=index == len(live) - 1,
                                     **kwargs)
            except requests.HTTPError as failure:
                status = getattr(failure.response, "status_code", None)
                if status != 429 or index == len(live) - 1:
                    raise
                self._closed[id(client)] = time.monotonic() + self.cooldown
                print(f"WARNING: {client.model} is rate limited on this key; "
                      f"trying the next route", file=sys.stderr)
                continue
            self._answered = client
            self._closed.pop(id(client), None)
            self._log.append(client.calls[-1])
            return result
        raise AssertionError("unreachable")


def build_pool(models, endpoint, key_envs, **settings):
    """A pool over every (model, key) pair, models in preference order.

    Named environment variables rather than keys, so a key never travels through an
    argument list and a missing one is reported by name.
    """
    keys = [(env, os.environ[env]) for env in key_envs if os.environ.get(env)]
    if not keys:
        raise ValueError(f"none of {', '.join(key_envs)} is set")
    return ClientPool([ChatClient(model=model, endpoint=endpoint, api_key=key, **settings)
                       for model in models for _, key in keys])
