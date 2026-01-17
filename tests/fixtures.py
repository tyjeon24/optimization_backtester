from pathlib import Path

import pandas as pd
import pytest

from src.bt.backtester import Backtester
from src.bt.indicators.bollinger_band import BollingerBand
from src.bt.indicators.compare_column import CompareColumn


@pytest.fixture
def backtester():
    models = [
        BollingerBand(),
        CompareColumn(left="Close", right="LowerBand", symbol="<", name="BuyBelowLowerBand", action="buy"),
        CompareColumn(left="Close", right="UpperBand", symbol=">", name="SellAboveUpperBand", action="sell"),
    ]
    aapl_data = pd.read_parquet("notebook/data/AAPL.parquet")
    msft_data = pd.read_parquet("notebook/data/MSFT.parquet")
    spy_data = pd.read_parquet("notebook/data/SPY.parquet")
    stocks = [aapl_data, msft_data]
    start = "2021-11-10"
    end = "2023-12-28"
    settings_path = Path("backtest_test.json")

    backtester = Backtester(
        models=models,
        stocks=stocks,
        stock_baseline=spy_data,
        start=start,
        end=end,
        settings_path=settings_path.absolute().as_posix(),
    )

    yield backtester

    settings_path.unlink(missing_ok=True)


@pytest.fixture(scope="module")
def backtester_fitted():
    models = [
        BollingerBand(),
        CompareColumn(left="Close", right="LowerBand", symbol="<", name="BuyBelowLowerBand", action="buy"),
        CompareColumn(left="Close", right="UpperBand", symbol=">", name="SellAboveUpperBand", action="sell"),
    ]
    aapl_data = pd.read_parquet("notebook/data/AAPL.parquet")
    msft_data = pd.read_parquet("notebook/data/MSFT.parquet")
    spy_data = pd.read_parquet("notebook/data/SPY.parquet")
    stocks = [aapl_data, msft_data]
    start = "2021-01-01"
    end = "2023-03-31"
    settings_path = Path("backtest_test.json")

    backtester = Backtester(
        models=models,
        stocks=stocks,
        stock_baseline=spy_data,
        start=start,
        end=end,
        settings_path=settings_path.absolute().as_posix(),
    )

    backtester.fit(5)
    backtester.predict(start=start)

    yield backtester

    settings_path.unlink(missing_ok=True)
