from src.metrics import sharpe_ratio, expectancy_r, profit_factor
import numpy as np

def test_expectancy_56_15R():
    assert abs(expectancy_r(0.56, 1.5) - 0.40) < 1e-9

def test_sharpe_zero_on_flat():
    assert sharpe_ratio(np.zeros(50)) == 0.0

def test_profit_factor():
    assert abs(profit_factor(np.array([1.5, 1.5, -1.0])) - 3.0) < 1e-9
