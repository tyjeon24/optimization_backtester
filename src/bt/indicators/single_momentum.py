import pandas as pd

from src.bt.indicators.base_indicator import BaseIndicator


class SingleMomentum(BaseIndicator):
    def __init__(self, period: int = 2, target: str = "Close", name: str = "SingleMomentum"):
        super().__init__()
        self.period = period
        self.name = name
        self.target = target
        self.parameters = []

    def pipe(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()[[self.target]]
        delta = data[self.target].diff().fillna(0)
        data["direction"] = delta.mask(delta > 0, 1).mask(delta < 0, -1)
        data["same_direction_group"] = (data["direction"] != data["direction"].shift()).cumsum()
        data[self.name] = data.groupby("same_direction_group").cumcount() + 1
        data.loc[data["direction"] == -1, self.name] *= -1
        df[self.name] = data[self.name]
        return df
