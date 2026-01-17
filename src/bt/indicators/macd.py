import pandas as pd

from src.bt.indicators.base_indicator import BaseIndicator


class MACD(BaseIndicator):
    """MACD = EMA(short) - EMA(long) = EMA(stock, 12days) - EMA(stock, 26days)
    MACD_Signal = EMA(MACD, 9days)
    """

    def __init__(
        self,
        period_short: int = 12,
        period_long: int = 26,
        period_signal: int = 9,
        use_exponential_moving_average: bool = True,  # basically MACD uses exponential moving average
        name_macd: str = "MACD",
        name_signal: str = "MACDSignal",
        target: str = "Close",
    ):
        super().__init__()
        self.period_short = period_short
        self.period_long = period_long
        self.period_signal = period_signal
        self.use_exponential_moving_average = use_exponential_moving_average
        self.name_macd = name_macd
        self.name_signal = name_signal
        self.target = target
        self.parameters = [
            {"name": "period_short", "type": "range", "bounds": [2, 4, 8, 12, 16, 20, 25], "value_type": "int"},
            {"name": "period_long", "type": "range", "bounds": [26, 32, 40, 64], "value_type": "int"},
            {"name": "period_signal", "type": "range", "bounds": [5, 7, 9, 10, 15, 20], "value_type": "int"},
            {"name": "use_exponential_moving_average", "type": "choice", "values": [True, False], "value_type": "bool"},
        ]

    def pipe(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.use_exponential_moving_average:
            short = df[self.target].ewm(span=self.period_short).mean()
            long = df[self.target].ewm(span=self.period_long).mean()
            df[self.name_macd] = short - long
            df[self.name_signal] = df[self.name_macd].ewm(span=self.period_signal).mean()
        else:
            short = df[self.target].rolling(span=self.period_short).mean()
            long = df[self.target].rolling(span=self.period_long).mean()
            df[self.name_macd] = short - long
            df[self.name_signal] = df[self.name_macd].rolling(self.period_signal).mean()
        return df


class MACDDivision(BaseIndicator):
    """원래는 short - long 인데, 나눗셈으로 MACD를 계산함.
    일반적인 방법은 아님. 그렇지만 일관된 공식을 적용하는 데는 이게 더 나음.
    MACD = EMA(short) / EMA(long) = EMA(stock, 12days) / EMA(stock, 26days)
    MACD_Signal = EMA(MACD, 9days)

    장점 : 일관된 공식 적용
    예를 들어 일반적인 뺼셈 기반 MACD의 경우 다음처럼 골든크로스가 발생하는 두 종목이 있다고 하자.
    그리고 두 종목은 실제로 미래 가격이 올랐기 때문에, 골든 크로스 떄 구매 신호를 확실히 하고 싶다고 하자.
    [-500 -> -200 -> 100 -> 400 -> 700] = [400-900, 600-800, 800-700, 1000-600, 1200-500]
    [-5 -> -2 -> 1 -> 4 -> 7] = [4-9, 6-8, 8-7, 10-6, 12-5]
    두 경우 하나의 공식을 넣고 돌리기 까다롭다.

    이때, 나눗셈 기반 MACD를 계산하면 아래와 같다.
    [0.44, 0.75, 1.14, 1.67, 2.4]
    [0.44, 0.75, 1.14, 1.67, 2.4]

    즉 변동성 자체에만 집중할 수 있게 해 준다.
    """

    def __init__(
        self,
        period_short: int = 12,
        period_long: int = 26,
        period_signal: int = 9,
        use_exponential_moving_average: bool = True,  # basically MACD uses exponential moving average
        name_macd: str = "MACD",
        name_signal: str = "MACDSignal",
        target: str = "Close",
    ):
        super().__init__()
        self.period_short = period_short
        self.period_long = period_long
        self.period_signal = period_signal
        self.use_exponential_moving_average = use_exponential_moving_average
        self.name_macd = name_macd
        self.name_signal = name_signal
        self.target = target
        self.parameters = [
            {"name": "period_short", "type": "choice", "values": [2, 4, 8, 12, 16, 20, 25], "value_type": "int"},
            {"name": "period_long", "type": "choice", "values": [26, 32, 40, 64], "value_type": "int"},
            {"name": "period_signal", "type": "choice", "values": [5, 7, 9, 10, 15, 20], "value_type": "int"},
            {"name": "use_exponential_moving_average", "type": "choice", "values": [True, False], "value_type": "bool"},
        ]

    def pipe(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.use_exponential_moving_average:
            short = df[self.target].ewm(span=self.period_short).mean()
            long = df[self.target].ewm(span=self.period_long).mean()
            df[self.name_macd] = short / long - 1
            df[self.name_signal] = df[self.name_macd].ewm(span=self.period_signal).mean()
        else:
            short = df[self.target].rolling(self.period_short).mean()
            long = df[self.target].rolling(self.period_long).mean()
            df[self.name_macd] = short / long - 1
            df[self.name_signal] = df[self.name_macd].rolling(self.period_signal).mean()
        return df
