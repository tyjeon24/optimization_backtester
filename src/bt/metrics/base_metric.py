import abc

import pandera as pa
from pandera.typing import DataFrame

from src.bt.schemas.portfolio import PortfolioSchema


class BaseMetric(metaclass=abc.ABCMeta):
    @pa.check_types
    @abc.abstractmethod
    def calculate(self, portfolio: DataFrame[PortfolioSchema]) -> float: ...
