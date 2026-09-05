"""Non-blocking reverse DNS lookups for the curses render path.

``cli.create_case_list()`` reformats every known case on every redraw, and a
redraw happens on every keypress.  A synchronous PTR lookup in that path
therefore costs one DNS round trip per BGP case per keystroke, which is what
made curitz unusable against a Zino server with a four-digit number of open
cases.

`ReverseResolver.lookup` never blocks.  It answers from an unbounded in-memory
cache, and on a miss it returns the address unchanged and hands the lookup to a
pool of worker threads.  The resolved name shows up on a later redraw.
"""

import logging
import queue
import threading
import time
from typing import Callable, Dict, List, NamedTuple, Set

log = logging.getLogger("cuRitz")

DEFAULT_TTL = 3600.0  # seconds an answer is considered fresh
DEFAULT_WORKERS = 4  # concurrent PTR lookups

CacheEntry = NamedTuple("CacheEntry", [("name", str), ("expires", float)])


class ReverseResolver:
    """Caching reverse resolver that never blocks its caller.

    :param resolve: callable taking an address string and returning a hostname.
        Called from worker threads only.  It may raise, and a raising lookup is
        cached as "unresolvable" for `ttl` seconds so a dead zone is queried at
        most once per TTL rather than once per redraw.  It must not block
        indefinitely: the pool has no timeout of its own, so a callable that
        hangs takes a worker with it until it returns.
    :param ttl: seconds before a cached answer is refreshed.
    :param workers: size of the background lookup pool.
    :param clock: monotonic time source, injectable for testing.
    """

    def __init__(
        self,
        resolve: Callable[[str], str],
        ttl: float = DEFAULT_TTL,
        workers: int = DEFAULT_WORKERS,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._resolve = resolve
        self._ttl = ttl
        self._workers = workers
        self._clock = clock

        self._cache: Dict[str, CacheEntry] = {}
        self._pending: Set[str] = set()
        self._queue: "queue.Queue[str]" = queue.Queue()
        self._lock = threading.Lock()
        self._threads: List[threading.Thread] = []

    def lookup(self, address) -> str:
        """Return the PTR name for `address`, or `address` itself if not known yet.

        Never blocks.  A miss, or an entry past its TTL, schedules a background
        lookup; a stale name keeps being served until that lookup lands, so the
        display does not flap back to a bare address on every refresh.

        :param address: IP address, as a string or anything `str()` accepts.
        :return: the resolved name, or the address as a string.
        """
        address = str(address)
        entry = self._cache.get(address)
        if entry is None or entry.expires <= self._clock():
            self._schedule(address)
        return entry.name if entry is not None else address

    def _schedule(self, address: str) -> None:
        """Queue `address` for a background lookup, unless one is already due."""
        with self._lock:
            if address in self._pending:
                return
            self._pending.add(address)
        # Queue before starting workers, so that an address is never left
        # pending-but-unqueued if the pool cannot be started
        self._queue.put(address)
        self._start_workers()

    def _start_workers(self) -> None:
        """Top the worker pool back up, starting it on first use.

        This runs on every miss, so it doubles as the recovery path: a worker
        lost to an error that escaped `_resolve_once` is replaced the next time
        a lookup is scheduled, rather than shrinking the pool for good.

        The threads are daemons.  They own no resources the process needs to
        release, and the main thread must be free to leave `curses.wrapper` and
        restore the terminal without waiting on a lookup in flight.
        """
        with self._lock:
            self._threads = [thread for thread in self._threads if thread.is_alive()]
            while len(self._threads) < self._workers:
                thread = threading.Thread(
                    target=self._work,
                    name="reverse-dns-{}".format(len(self._threads)),
                    daemon=True,
                )
                try:
                    thread.start()
                except RuntimeError:
                    # Out of threads.  Whatever is queued stays queued, and
                    # lookup() keeps handing out bare addresses in the meantime
                    log.error("Could not start a reverse DNS worker", exc_info=True)
                    return
                self._threads.append(thread)

    def _work(self) -> None:
        while True:
            self._resolve_once(self._queue.get())

    def _resolve_once(self, address: str) -> None:
        """Resolve one address and cache whatever came of it.

        An address that cannot be resolved is cached as its own name, which is
        what `lookup` would have returned anyway, so a dead zone costs one
        query per TTL instead of one per redraw.

        :param address: the address to look up.
        """
        name = address
        try:
            name = str(self._resolve(address))
        except Exception:
            log.debug("Reverse lookup of %s failed", address, exc_info=True)
        finally:
            # In a finally so that an error escaping the except above cannot
            # strand the address in _pending, where nothing would retry it
            self._store(address, name)

    def _store(self, address: str, name: str) -> None:
        self._cache[address] = CacheEntry(name, self._clock() + self._ttl)
        with self._lock:
            self._pending.discard(address)
