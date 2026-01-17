from pandera.typing import DataFrame

from src.bt.schemas.portfolio import PortfolioSchema

from .base_metric import BaseMetric


class MDD(BaseMetric):
    def calculate(self, portfolio: DataFrame[PortfolioSchema]) -> float:
        cumulative_max = portfolio["Portfolio"].cummax()
        drawdown = (portfolio["Portfolio"] - cumulative_max) / cumulative_max * 100.0
        mdd = abs(drawdown.min())
        return mdd
