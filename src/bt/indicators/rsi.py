import pandas as pd

from src.bt.indicators.base_indicator import BaseIndicator


class RSI(BaseIndicator):
    def __init__(self, period: int = 20, name: str = "RSI", target: str = "Close"):
        super().__init__()
        self.period = period
        self.name = name
        self.target = target
        self.parameters = [
            {"name": "period", "type": "choice", "values": [2, 4, 8, 12, 16, 20, 26, 32, 64, 128], "value_type": "int"},
        ]

    def pipe(self, df: pd.DataFrame) -> pd.DataFrame:
        delta = df[self.target].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        average_gain = gain.rolling(self.period).mean()
        average_loss = loss.rolling(self.period).mean()

        df[self.name] = 100 - (100 / (1 + average_gain / average_loss))
        return df
