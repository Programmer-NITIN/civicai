"""
tests/test_middleware_edge.py
-------------------------------
Edge case tests for the rate limiter middleware.
"""

import time
from app.middleware.rate_limiter import make_rate_limiter, _SlidingWindowRateLimiter


class TestRateLimiterInternals:
    def test_factory_returns_limiter(self):
        limiter = make_rate_limiter(10, 60)
        assert isinstance(limiter, _SlidingWindowRateLimiter)

    def test_slots_defined(self):
        limiter = make_rate_limiter(5)
        assert hasattr(limiter, "max_requests")
        assert hasattr(limiter, "window_seconds")
        assert hasattr(limiter, "store")

    def test_default_window_seconds(self):
        limiter = make_rate_limiter(10)
        assert limiter.window_seconds == 60

    def test_custom_window(self):
        limiter = make_rate_limiter(5, window_seconds=120)
        assert limiter.window_seconds == 120

    def test_store_is_empty_initially(self):
        limiter = make_rate_limiter(5)
        assert len(limiter.store) == 0

    def test_clear_resets_store(self):
        limiter = make_rate_limiter(5)
        limiter.store["test_ip"].append(time.time())
        assert len(limiter.store) == 1
        limiter.store.clear()
        assert len(limiter.store) == 0
