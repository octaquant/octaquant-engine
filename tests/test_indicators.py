from octaquant.strategy.indicators import ema, fib_retracement


def test_ema_returns_value():
    series = list(range(1, 40))
    assert ema(series, period=26) is not None


def test_fib_retracement_level():
    value = fib_retracement(100.0, 200.0, 0.618)
    assert round(value, 2) == 138.2
