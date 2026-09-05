import threading
import time

import pytest

from curitz.reverse_dns import DEFAULT_TTL, ReverseResolver


class TestLookup:
    def test_when_the_address_is_unknown_it_should_return_the_address_itself(
        self, resolver
    ):
        assert resolver.lookup("192.0.2.1") == "192.0.2.1"

    def test_when_the_address_is_unknown_it_should_not_call_the_backend_inline(
        self, resolver, backend
    ):
        resolver.lookup("192.0.2.1")

        assert backend.calls == []

    def test_when_the_background_lookup_has_landed_it_should_return_the_name(
        self, resolver, drain
    ):
        resolver.lookup("192.0.2.1")
        drain()

        assert resolver.lookup("192.0.2.1") == "host1.example.org"

    def test_when_the_name_is_cached_it_should_not_look_it_up_again(
        self, resolver, backend, drain
    ):
        resolver.lookup("192.0.2.1")
        drain()
        resolver.lookup("192.0.2.1")
        drain()

        assert backend.calls == ["192.0.2.1"]

    def test_when_the_same_address_is_looked_up_repeatedly_it_should_queue_it_once(
        self, resolver, backend, drain
    ):
        for _ in range(10):
            resolver.lookup("192.0.2.1")
        drain()

        assert backend.calls == ["192.0.2.1"]

    def test_when_the_address_is_not_a_string_it_should_still_resolve_it(
        self, resolver, drain
    ):
        class Address:
            def __str__(self):
                return "192.0.2.1"

        resolver.lookup(Address())
        drain()

        assert resolver.lookup("192.0.2.1") == "host1.example.org"


class TestLookupWhenTheBackendFails:
    def test_it_should_serve_the_address_as_its_own_name(
        self, resolver, backend, drain
    ):
        backend.fail = True

        resolver.lookup("192.0.2.1")
        drain()

        assert resolver.lookup("192.0.2.1") == "192.0.2.1"

    def test_it_should_not_retry_until_the_entry_goes_stale(
        self, resolver, backend, drain, clock
    ):
        backend.fail = True

        resolver.lookup("192.0.2.1")
        drain()
        resolver.lookup("192.0.2.1")
        drain()
        assert backend.calls == ["192.0.2.1"]

        clock.advance(DEFAULT_TTL + 1)
        resolver.lookup("192.0.2.1")
        drain()
        assert backend.calls == ["192.0.2.1", "192.0.2.1"]


class TestLookupOnExpiry:
    def test_when_the_entry_is_stale_it_should_refresh_it(
        self, resolver, backend, drain, clock
    ):
        resolver.lookup("192.0.2.1")
        drain()

        clock.advance(DEFAULT_TTL + 1)
        resolver.lookup("192.0.2.1")
        drain()

        assert backend.calls == ["192.0.2.1", "192.0.2.1"]

    def test_when_the_entry_is_stale_it_should_keep_serving_the_old_name(
        self, resolver, drain, clock
    ):
        resolver.lookup("192.0.2.1")
        drain()

        clock.advance(DEFAULT_TTL + 1)

        assert resolver.lookup("192.0.2.1") == "host1.example.org"


class TestWorkerPool:
    """The one place the real threads run, since everything above stubs them out."""

    def test_when_a_lookup_is_scheduled_it_should_resolve_in_the_background(self):
        resolver = ReverseResolver(lambda address: "host.example.org")

        assert resolver.lookup("192.0.2.1") == "192.0.2.1"

        assert wait_for(lambda: resolver.lookup("192.0.2.1") == "host.example.org")

    def test_when_a_worker_dies_a_later_lookup_should_still_resolve(self, monkeypatch):
        monkeypatch.setattr(threading, "excepthook", lambda args: None)
        resolver = ReverseResolver(kills_the_worker_on, workers=1)

        resolver.lookup("192.0.2.1")
        assert wait_for(
            lambda: not any(thread.is_alive() for thread in resolver._threads)
        ), "the worker was supposed to die"

        resolver.lookup("192.0.2.2")

        assert wait_for(lambda: resolver.lookup("192.0.2.2") == "host.example.org")

    def test_when_a_worker_dies_it_should_not_strand_the_address(self, monkeypatch):
        monkeypatch.setattr(threading, "excepthook", lambda args: None)
        resolver = ReverseResolver(kills_the_worker_on, workers=1)

        resolver.lookup("192.0.2.1")

        assert wait_for(lambda: not resolver._pending)


@pytest.fixture
def resolver(backend, clock, monkeypatch):
    """A resolver whose worker pool never starts.

    Queued lookups then run only when the test says `drain()`, which keeps
    these tests free of real threads and real timing.  `TestWorkerPool` covers
    what is stubbed out here.
    """
    monkeypatch.setattr(ReverseResolver, "_start_workers", lambda self: None)
    return ReverseResolver(backend, clock=clock)


@pytest.fixture
def drain(resolver):
    """Run every queued lookup on the calling thread, through the real code."""

    def _drain():
        while not resolver._queue.empty():
            resolver._resolve_once(resolver._queue.get())

    return _drain


@pytest.fixture
def backend():
    return FakeBackend()


@pytest.fixture
def clock():
    return FakeClock()


class FakeBackend:
    """A stand-in for the blocking PTR lookup, driven by the test."""

    def __init__(self):
        self.calls = []
        self.fail = False

    def __call__(self, address):
        self.calls.append(address)
        if self.fail:
            raise OSError("no such domain")
        return "host{}.example.org".format(address.rsplit(".", 1)[-1])


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def kills_the_worker_on(address):
    """Raise something `_resolve_once` does not catch, for the one address."""
    if address == "192.0.2.1":
        raise BaseException("takes the worker thread with it")
    return "host.example.org"


def wait_for(predicate, timeout=5):
    """Poll `predicate` until it holds, or `timeout` seconds pass."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.01)
    return False
