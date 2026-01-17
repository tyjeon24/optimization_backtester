from pandera.typing import DataFrame

from src.bt.metrics.cagr import CAGR
from src.bt.metrics.mdd import MDD
from src.bt.schemas.portfolio import PortfolioSchema

from .base_metric import BaseMetric


class CalmarRatio(BaseMetric):
    def calculate(self, portfolio: DataFrame[PortfolioSchema]) -> float:
        cagr = CAGR()
        mdd = MDD()
        cagr_value = cagr.calculate(portfolio)
        mdd_value = mdd.calculate(portfolio)
        calmar = cagr_value / (mdd_value + 0.0001)
        return calmar
