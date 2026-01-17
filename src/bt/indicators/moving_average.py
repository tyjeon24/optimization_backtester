import pandas as pd

from src.bt.indicators.base_indicator import BaseIndicator


class MovingAverage(BaseIndicator):
    def __init__(
        self,
        period: int = 20,
        use_exponential_moving_average: bool = False,
        name: str = "MovingAverage",
        target: str = "Close",
    ):
        super().__init__()
        self.name = name
        self.period = period
        self.use_exponential_moving_average = use_exponential_moving_average
        self.target = target
        self.parameters = [
            {"name": "period", "type": "choice", "values": [2, 4, 8, 12, 16, 20, 26, 32, 64, 128], "value_type": "int"},
            {"name": "use_exponential_moving_average", "type": "choice", "values": [True, False], "value_type": "bool"},
        ]

    def pipe(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.use_exponential_moving_average:
            df[self.name] = df[self.target].ewm(span=self.period).mean()
        else:
            df[self.name] = df[self.target].rolling(self.period).mean()
        return df
