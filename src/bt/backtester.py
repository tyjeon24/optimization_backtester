from datetime import datetime, timedelta

import pandas as pd
import pandera as pa
from pandera.typing import DataFrame

import wandb
from src.bt.indicators.base_indicator import BaseIndicator
from src.bt.metrics.alpha import Alpha
from src.bt.metrics.cagr import CAGR
from src.bt.metrics.mdd import MDD
from src.bt.schemas.loss import LossSchema
from src.bt.schemas.portfolio import PortfolioSchema
from src.bt.schemas.stock import StockSchema

from .optimizer import Optimizer
from .strategy_model import StrategyModel

WANDB_BASE_URL = "http://172.18.209.39:37511"
WANDB_API_KEY = "local-8919e40e3ddd926a14793a87aa1b770b6d877d38"  # aaaa@aaaa.com / aaaaaaaa


class Backtester:
    @pa.check_types
    def __init__(
        self,
        models: list[BaseIndicator],
        stocks: list[DataFrame[StockSchema]],
        stock_baseline: DataFrame[StockSchema],
        start: str,
        end: str,
        metric: str = "loss",
        constraints: list[str] = [],
        verbose: bool = False,
        settings_path: str = "backtest.json",
        skip_cushion_data: bool = True,
    ):
        self.models = models
        self.strategy_model = StrategyModel(self.models)
        self.stocks = stocks
        self.stock_baseline = stock_baseline
        self.metric = metric
        self.start = start
        self.end = end
        self.constraints = constraints
        self.verbose = verbose
        self.settings_path = settings_path
        self.skip_cushion_data = skip_cushion_data

        self.portfolio_values = None
        self.book_data = []

    def fit(self, n_trials: int = 100, early_stop: int = 30):
        self.optimizer = Optimizer(
            parameters=self.strategy_model.parameters,
            evaluate=self.evaluate,
            objectives=self.metric,
            verbose=self.verbose,
            settings_path=self.settings_path,
        )

        self.optimizer.optimize(n_trials, early_stop)

    def evaluate(self, x: dict[str, float | int | bool] = {}) -> dict:
        """목적 함수의 계산값을 반환합니다.

        Args:
            x (dict, optional): x는 각 BaseIndicator의 parameter 값입니다. Defaults to {}.

        Returns:
            dict: 손실 함수 값을 반환합니다.
        """
        self.alphas: list[float] = []
        self.cagrs: list[float] = []
        self.mdds: list[float] = []

        self.strategy = self.strategy_model.create_strategy(x, self.models)
        self.stocks_with_indicators = [self.create_stock_indicator(stock, self.strategy) for stock in self.stocks]

        wandb.login(key=WANDB_API_KEY, host=WANDB_BASE_URL)
        wandb.init(project="myproj2", config=x)
        self.sliding_test()
        wandb.finish()
        loss_schema = self.calculate_loss()
        return loss_schema.__dict__

    def sliding_test(self):
        trading_book = pd.concat(self.stocks_with_indicators.copy(), axis=0)
        trading_book = trading_book.sort_values(["Date", "Volume"], ascending=[True, False])
        for start, end in DateSlider(
            start=datetime.strptime(self.start, "%Y-%m-%d"),
            end=datetime.strptime(self.end, "%Y-%m-%d"),
            sliding_duration=timedelta(days=30),
            backtest_duraton=timedelta(days=730),
        ):
            portfolio = self.calculate_portfolio_values(
                trading_book.loc[(trading_book["Date"] >= start) & (trading_book["Date"] <= end), :].copy(),
                start,
                end,
            )
            self.append_metrics(portfolio)

    @pa.check_types
    def append_metrics(self, portfolio: DataFrame[PortfolioSchema]) -> None:
        cagr = CAGR()
        alpha = Alpha()
        mdd = MDD()

        self.alphas.append(alpha.calculate(portfolio))
        self.cagrs.append(cagr.calculate(portfolio))
        self.mdds.append(mdd.calculate(portfolio))
        wandb.log({"train/cagr": self.cagrs[-1]})
        wandb.log({"train/alpha": self.alphas[-1]})
        wandb.log({"train/mdd": self.mdds[-1]})
        wandb.log({"train/mean_alpha": sum(self.alphas) / len(self.alphas)})
        wandb.log({"train/mean_cagr": sum(self.cagrs) / len(self.cagrs)})
        wandb.log({"train/worst_alpha": min(self.alphas)})
        wandb.log({"train/worst_cagr": min(self.cagrs)})
        wandb.log({"train/worst_mdd": max(self.mdds)})

    def calculate_loss(self) -> LossSchema:
        mean_alpha_to_minimize = -1 * self.metrics["mean_alpha"]  # multiply -1 to minimize
        alpha_regularization = max(0, -1 * self.metrics["worst_alpha"]) ** 2
        mdd_regularization = max(0, self.metrics["worst_mdd"] - 30) ** 2
        cagr_regularization = max(0, -1 * self.metrics["worst_cagr"]) ** 2

        loss_schema = LossSchema(
            loss=mean_alpha_to_minimize + alpha_regularization + mdd_regularization + cagr_regularization
        )
        return loss_schema

    def create_stock_indicator(self, stock: pd.DataFrame, strategy: dict[str, list[BaseIndicator]]) -> pd.DataFrame:
        trading_book = stock.copy()
        for step in strategy.values():
            for indicator in step:
                trading_book.pipe(indicator.pipe)
        trading_book.pipe(self.add_action_columns, strategy=strategy)

        return trading_book

    def add_action_columns(self, trading_book: pd.DataFrame, strategy: dict[str, list[BaseIndicator]]) -> pd.DataFrame:
        buy_columns = [indicator.name for indicator in strategy["buy"]]
        sell_columns = [indicator.name for indicator in strategy["sell"]]
        trading_book["BuyAction"] = trading_book.loc[:, buy_columns].sum(axis=1)
        trading_book["SellAction"] = trading_book.loc[:, sell_columns].sum(axis=1)
        if self.skip_cushion_data:
            trading_book.loc[trading_book.isna().any(axis=1), "BuyAction"] = 0
            trading_book.loc[trading_book.isna().any(axis=1), "SellAction"] = 0

        return trading_book

    @pa.check_types
    def calculate_portfolio_values(
        self, trading_book: pd.DataFrame, start: str, end: str, cash: float = 10000.0
    ) -> DataFrame[PortfolioSchema]:
        stock: dict[str, int] = {}
        tax = 0.001  # 0.1% 구매, 판매 수수료
        portfolio_stock_price: dict[str, float] = {}  # 평단가
        ratio_to_buy = 0.1
        portfolio_values: list[float] = []

        stock_baseline = self.stock_baseline.copy()
        stock_baseline = stock_baseline.loc[(stock_baseline["Date"] >= start) & (stock_baseline["Date"] <= end), :]
        trade_rows = []
        baseline_prices = []
        baseline_stock_number = cash // stock_baseline.iloc[0]["Close"]
        baseline_cash_remainder = cash - baseline_stock_number * stock_baseline.iloc[0]["Close"]

        for date, book_day in trading_book.groupby("Date"):
            if len(portfolio_values):
                portfolio_value = portfolio_values[-1]
            else:
                portfolio_value = cash

            for _, row in book_day.iterrows():
                close_price = row["Close"]
                price_with_tax = close_price * (1 + tax)
                ticker = row["Ticker"]

                buy_condition = row["BuyAction"] - row["SellAction"] > 0.5
                sell_condition = stock.get(ticker, None) and row["BuyAction"] - row["SellAction"] < -0.5

                if buy_condition:
                    if cash < price_with_tax:
                        # do not buy, just write on trading book.
                        row = {
                            "Date": date,
                            "Action": "Buy",
                            "Strength": row["BuyAction"] - row["SellAction"],
                            "Ticker": ticker,
                            "Price": close_price,
                            "PortfolioPrice": portfolio_stock_price.get(ticker, 0),
                            "Quantity": 0,
                            "Tax": 0,
                            "Cash": cash,
                            "Margin": 0,  # only valid of for sell
                            "PortfolioValue": portfolio_value,
                        }
                    else:
                        number_to_buy = max(1, (cash * ratio_to_buy) // price_with_tax)
                        cash -= price_with_tax * number_to_buy
                        # 평단가 계산
                        # 평단가 = (구매전평균가*보유주 + 현재종가*신규주) / 합산주식수
                        portfolio_stock_price[ticker] = (
                            portfolio_stock_price.get(ticker, 0) * stock.get(ticker, 0) + close_price * number_to_buy
                        ) / (stock.get(ticker, 0) + number_to_buy)
                        stock[ticker] = stock.get(ticker, 0) + number_to_buy
                        row = {
                            "Date": date,
                            "Action": "Buy",
                            "Strength": row["BuyAction"] - row["SellAction"],
                            "Ticker": ticker,
                            "Price": close_price,
                            "PortfolioPrice": portfolio_stock_price[ticker],
                            "Quantity": number_to_buy,
                            "Tax": close_price * tax * number_to_buy,
                            "Cash": cash,
                            "Margin": 0,  # only valid of for sell
                            "PortfolioValue": portfolio_value,
                        }
                    trade_rows.append(row)

                elif sell_condition:
                    cash += stock[ticker] * (close_price * (1 - tax))
                    row = {
                        "Date": date,
                        "Action": "Sell",
                        "Strength": row["BuyAction"] - row["SellAction"],
                        "Ticker": ticker,
                        "Price": close_price,
                        "PortfolioPrice": portfolio_stock_price.get(ticker, 0),
                        "Quantity": stock[ticker],
                        "Tax": close_price * tax * stock[ticker],
                        "Cash": cash,
                        "Margin": stock[ticker] * (close_price * (1 - tax) - portfolio_stock_price.get(ticker, 0)),
                        "PortfolioValue": portfolio_value,
                    }
                    trade_rows.append(row)
                    stock[ticker] = 0
                    portfolio_stock_price[ticker] = 0

            # 하루치 book 순환이 끝나면 포트폴리오 업데이트
            portfolio_value = cash
            for ticker, number in stock.items():
                close_price_today = book_day.loc[book_day["Ticker"] == ticker, "Close"].to_numpy().item()
                portfolio_value += number * close_price_today
            portfolio_values.append(portfolio_value)

            baseline_portfolio_value = baseline_cash_remainder
            baseline_price_today = stock_baseline.loc[stock_baseline["Date"] == date, "Close"].to_numpy().item()
            baseline_portfolio_value += baseline_stock_number * baseline_price_today
            baseline_prices.append(baseline_portfolio_value)

        self.portfolio_values = pd.Series(portfolio_values, index=trading_book.Date.unique())
        self.baseline_values = pd.Series(baseline_prices, index=trading_book.Date.unique())
        if len(trade_rows):
            self.trade = pd.DataFrame(trade_rows)
        else:
            self.trade = pd.DataFrame(
                columns=[
                    "Date",
                    "Action",
                    "Ticker",
                    "Price",
                    "PortfolioPrice",
                    "Quantity",
                    "Cash",
                    "Margin",
                    "PortfolioValue",
                ]
            )
        portfolio = pd.concat([self.portfolio_values, self.baseline_values], axis=1).reset_index()
        portfolio.columns = ["Date", "Portfolio", "Baseline"]
        return portfolio

    def predict(self, start: str, parameters: dict[str, float | int | bool] | None = None) -> dict[str, pd.DataFrame]:
        if parameters is None:
            parameters, _ = self.optimizer.client.get_best_parameters()
        self.strategy = self.strategy_model.create_strategy(parameters, self.models)
        end = "20350101"  # TODO 적절한 값으로 대체
        self.stocks_with_indicators = [self.create_stock_indicator(stock, self.strategy) for stock in self.stocks]

        trading_book = pd.concat(self.stocks_with_indicators.copy(), axis=0).sort_values(
            ["Date", "Volume"], ascending=[True, False]
        )
        portfolio = self.calculate_portfolio_values(
            trading_book.loc[(trading_book["Date"] >= start) & (trading_book["Date"] <= end), :].copy(),
            start,
            end,
        )

        self.prediction = {"trade": self.trade, "portfolio": portfolio}
        return self.prediction


class DateSlider:
    def __init__(
        self,
        start: datetime,
        end: datetime,
        sliding_duration: timedelta = timedelta(days=7),
        backtest_duraton: timedelta = timedelta(days=730),
    ):
        """Sliding 백테스팅을 진행할 시작 기간과 끝 기간을 제공하는 Generator입니다.

        백테스팅 시 sliding window가 필요한 경우가 생깁니다.
        예를 들어 [1일-4일, 3일-6일, 5일-8일, 7-10일]처럼 간격 2일, 길이 3일의 백테스팅을 필요할 수 있습니다.
        이 경우 DateSlider(start, end, sliding_duration=timedelta(days=2), backtest_duraton=timedelta(days=3))의 제네레이터를 선언할 수 있습니다.

        ```
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 11)
        sliding_duration = timedelta(days=2)
        backtest_duraton = timedelta(days=3)

        slider = DateSlider(start, end, sliding_duration, backtest_duraton)
        for start, end in slider:
            print(start, "~", end)

        # 2024-01-01 00:00:00 2024-01-04 00:00:00
        # 2024-01-03 00:00:00 2024-01-06 00:00:00
        # 2024-01-05 00:00:00 2024-01-08 00:00:00
        # 2024-01-07 00:00:00 2024-01-10 00:00:00
        ```

        Args:
            start: 시작일입니다.
            end: 종료일입니다. 만약 백테스팅 시작일 + backtest_duraton > end이라면 종료합니다.
            sliding_duration: 시작 일자를 미는 간격입니다. timedelta(days=2)라면 시작일은 n일 → n+2일 → n+4일로 갱신됩니다.
            backtest_duraton: 하나의 백테스팅을 수행할 길이입니다.

        Examples:
            ```python
            start = datetime.now() - timedelta(days=10)
            end = datetime.now()

            slider = DateSlider(start, end)
            for start, end in slider:
                print(start, end)

            # 2025-01-11 10:41:24.688488 2025-01-18 10:41:24.688488
            ```
        """
        self.start = start
        self.end = end
        self.sliding_duration = sliding_duration
        self.backtest_duraton = backtest_duraton

    def __iter__(self):
        start = self.start
        while True:
            end = start + self.backtest_duraton
            if end > self.end:
                break
            yield start, end
            start += self.sliding_duration
