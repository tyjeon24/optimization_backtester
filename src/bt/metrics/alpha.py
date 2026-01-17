from pandera.typing import DataFrame

from src.bt.schemas.portfolio import PortfolioSchema

from .base_metric import BaseMetric


class Alpha(BaseMetric):
    def calculate(self, portfolio: DataFrame[PortfolioSchema]) -> float:
        portfolio_ratio = portfolio["Portfolio"].iloc[-1] / portfolio["Portfolio"].iloc[0]
        baseline_ratio = portfolio["Baseline"].iloc[-1] / portfolio["Baseline"].iloc[0]

        alpha = (portfolio_ratio - baseline_ratio) * 100
        return alpha
