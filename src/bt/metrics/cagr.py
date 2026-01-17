from pandera.typing import DataFrame

from src.bt.schemas.portfolio import PortfolioSchema

from .base_metric import BaseMetric


class CAGR(BaseMetric):
    def calculate(self, portfolio: DataFrame[PortfolioSchema]) -> float:
        initial_value = portfolio["Portfolio"].iloc[0]
        final_value = portfolio["Portfolio"].iloc[-1]

        start_date = portfolio["Date"].iloc[0]
        end_date = portfolio["Date"].iloc[-1]
        days = (end_date - start_date).days
        years = days / 365.25

        if years <= 0:
            return 0.0

        cagr = (final_value / initial_value) ** (1 / years) - 1
        return cagr * 100.0
