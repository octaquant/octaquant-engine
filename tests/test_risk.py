from octaquant.strategy.risk import monte_carlo_risk_of_ruin


def test_monte_carlo_output_bounds():
    result = monte_carlo_risk_of_ruin(
        iterations=10_000,
        initial_capital=100_000,
        risk_per_trade=0.01,
        win_rate=0.5,
        rr=2.0,
    )
    assert 0.0 <= result.risk_of_ruin <= 1.0
