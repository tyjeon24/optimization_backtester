import pandas as pd

from src.bt.indicators.base_indicator import BaseIndicator


class BollingerBand(BaseIndicator):
    def __init__(
        self,
        period: int = 20,
        upper_multiplier: float = 2.0,
        lower_multiplier: float = 2.0,
        use_exponential_moving_average=False,
        moving_average_name: str = "MiddleBand",
        upper_band_name: str = "UpperBand",
        lower_band_name: str = "LowerBand",
        band_gap_name: str = "BandGap",
        target: str = "Close",
    ):
        super().__init__()
        self.moving_average_name = moving_average_name
        self.upper_band_name = upper_band_name
        self.lower_band_name = lower_band_name
        self.band_gap_name = band_gap_name
        self.period = period
        self.upper_multiplier = upper_multiplier
        self.lower_multiplier = lower_multiplier
        self.use_exponential_moving_average = use_exponential_moving_average
        self.target = target
        self.parameters = [
            # {"name": "period", "type": "range", "bounds": [2, 120], "value_type": "int"},
            # {"name": "upper_multiplier", "type": "range", "bounds": [0.1, 3], "value_type": "float"},
            # {"name": "lower_multiplier", "type": "range", "bounds": [0.1, 3], "value_type": "float"},
            {"name": "period", "type": "choice", "values": [2, 4, 8, 12, 16, 20, 26, 32, 64, 128], "value_type": "int"},
            {
                "name": "upper_multiplier",
                "type": "choice",
                "values": [0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
                "value_type": "float",
            },
            {
                "name": "lower_multiplier",
                "type": "choice",
                "values": [0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
                "value_type": "float",
            },
            {"name": "use_exponential_moving_average", "type": "choice", "values": [True, False], "value_type": "bool"},
        ]

    def pipe(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.use_exponential_moving_average:
            df[self.moving_average_name] = df[self.target].ewm(span=self.period).mean()
            standard_deviation = df[self.target].ewm(self.period).std()
        else:
            df[self.moving_average_name] = df[self.target].rolling(self.period).mean()
            standard_deviation = df[self.target].rolling(self.period).std()
        df[self.upper_band_name] = df[self.moving_average_name] + (self.upper_multiplier * standard_deviation)
        df[self.lower_band_name] = df[self.moving_average_name] - (self.lower_multiplier * standard_deviation)
        df[self.band_gap_name] = df[self.upper_band_name] / df[self.lower_band_name]
        return df
