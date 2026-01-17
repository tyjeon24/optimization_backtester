import abc
from typing import final

import pandas as pd


class BaseIndicator(metaclass=abc.ABCMeta):
    def __init__(self) -> None:
        self.prefix = None
        self.name: str = ""

    @abc.abstractmethod
    def pipe(self, df: pd.DataFrame) -> pd.DataFrame: ...

    @final
    def get_parameters(self, prefix: str):
        # Should be formatted for ax-platform.
        self.prefix = prefix
        prefixed_parameters = self.parameters.copy()
        for parameter in prefixed_parameters:
            parameter["name"] = self.prefix + parameter["name"]
        return prefixed_parameters

    @final
    def update_with_prefixed_params(self, params: dict):
        for key, value in params.items():
            if key.startswith(self.prefix):
                self.__setattr__(key.replace(self.prefix, ""), value)
