# flaky:不稳定的，易出故障的。
import pytest

_attempt = 0

@pytest.mark.flaky(reruns=3)
def test_flaky_demo():
    global _attempt
    _attempt += 1
    assert _attempt >=3