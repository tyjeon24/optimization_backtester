import pandas as pd

from src.bt.indicators.base_indicator import BaseIndicator


class CompareColumn(BaseIndicator):
    def __init__(self, name: str, action: str, left: str, symbol: str, right: str, multiplier: float = 1.0):
        super().__init__()
        self.name = name
        self.action = action
        self.left = left
        self.symbol = symbol
        self.right = right
        self.multiplier = multiplier
        self.parameters = [{"name": "multiplier", "type": "range", "bounds": [0.01, 1], "value_type": "float"}]

    def pipe(self, df: pd.DataFrame) -> pd.DataFrame:
        condition = f"{self.left} {self.symbol} {self.right}"
        df[self.name] = df.eval(condition) * self.multiplier
        return df
