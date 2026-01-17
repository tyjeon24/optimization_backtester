from typing import Any

from src.bt.indicators.base_indicator import BaseIndicator


class StrategyModel:
    def __init__(self, models: list[BaseIndicator]):
        self.models = models
        self.parameters = self.setup_parameters(self.models)

    def setup_parameters(self, models: list[BaseIndicator]) -> list[dict[str, Any]]:
        """각 모델의 self.parameters를 참조하여 ax 최적화용 파라미터를 설정합니다.

        Returns:
            dict: ax client의 create_experiment(parameters) 인자에 들어가는 값입니다.

        parameters 예시는 아래와 같습니다.
        [
            {'name': '0_BollingerBand_period',
            'type': 'choice',
            'values': [4, 14, 24, 34, 44, 54, 64, 74, 84, 94, 104, 114],
            'value_type': 'int'},
            {'name': '0_BollingerBand_upper_multiplier',
            'type': 'choice',
            'values': [0.1, 0.6, 1.1, 1.6, 2.1, 2.6, 3.1],
            'value_type': 'float'}
        ]
        """
        parameters = []
        for idx, model in enumerate(models):
            prefix = f"{idx}_{model.__dict__.get('name', type(model).__name__)}_"
            parameter = model.get_parameters(prefix=prefix)
            parameters.extend(parameter)
        return parameters

    def create_strategy(self, x: dict, models: list[BaseIndicator]) -> dict[str, list[BaseIndicator]]:
        strategy = {"setup": [], "buy": [], "sell": []}
        for model in models:
            model.update_with_prefixed_params(x)
            stage = model.__dict__.get("action", "setup")
            strategy[stage].append(model)
        return strategy
