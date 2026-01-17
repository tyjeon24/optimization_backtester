import pandas as pd

from src.bt.indicators.base_indicator import BaseIndicator


class CompareValue(BaseIndicator):
    def __init__(
        self,
        name: str,
        action: str,
        left: str,
        symbol: str,
        right: float | None = None,
        bound_min: float = -100.0,
        bound_max: float = 100.0,
        multiplier: float = 1.0,
    ):
        super().__init__()
        self.name = name
        self.action = action
        self.left = left
        self.symbol = symbol
        self.right = right
        self.multiplier = multiplier
        self.bound_min = bound_min * 1.0
        self.bound_max = bound_max * 1.0
        self.parameters = [
            {"name": "right", "type": "range", "bounds": [self.bound_min, self.bound_max], "value_type": "float"},
            {"name": "multiplier", "type": "range", "bounds": [0.01, 1], "value_type": "float"},
        ]

    def pipe(self, df: pd.DataFrame) -> pd.DataFrame:
        condition = f"{self.left} {self.symbol} {self.right}"
        df[self.name] = df.eval(condition) * self.multiplier
        return df
