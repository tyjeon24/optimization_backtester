import logging
import warnings
from pathlib import Path

import pandas as pd
import torch
from ax.service.ax_client import AxClient, ObjectiveProperties
from tqdm import tqdm

from src.bt.core.logging_config import logger


class Optimizer:
    def __init__(
        self,
        parameters,
        evaluate,
        objectives: str,
        parameter_constraints=None,
        outcome_constraints=None,
        verbose=False,
        settings_path: str | None = None,
    ):
        self.parameters = parameters
        self.evaluate = evaluate
        self.objectives = [objectives]
        self.parameter_constraints = parameter_constraints
        self.outcome_constraints = outcome_constraints
        self.verbose = verbose
        self.settings_path = settings_path
        self._setup()

    def _setup(self) -> None:
        if not self.verbose:
            warnings.filterwarnings("ignore")
            logging.getLogger("ax.core.experiment").setLevel(logging.ERROR)
            logging.getLogger("ax.modelbridge.dispatch_utils").setLevel(logging.ERROR)
            logging.getLogger("ax.service.utils.instantiation").setLevel(logging.ERROR)
            logging.getLogger("ax.service.utils.report_utils").setLevel(logging.ERROR)

        if self.settings_path is not None and Path(self.settings_path).exists():
            self.client = AxClient.load_from_json_file(self.settings_path)
        else:
            torch_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self._objective_targets = {objective: ObjectiveProperties(minimize=True) for objective in self.objectives}
            self.client = AxClient(verbose_logging=self.verbose, torch_device=torch_device)

            self.client.create_experiment(
                parameters=self.parameters,
                objectives=self._objective_targets,
                parameter_constraints=self.parameter_constraints,
                outcome_constraints=self.outcome_constraints,
            )

        if self.settings_path:
            self.client.save_to_json_file(self.settings_path)

    def optimize(self, n: int, early_stop: int = 10, return_sorted: bool = False) -> pd.DataFrame:
        for i in tqdm(range(n)):
            parameterization, trial_index = self.client.get_next_trial()
            self.client.complete_trial(trial_index=trial_index, raw_data=self.evaluate(parameterization))
            if self.settings_path and i % 50 == 0:
                self.client.save_to_json_file(self.settings_path)

            # check early stop condition
            if self.is_early_stop_condition(i, early_stop):
                break

        return self.show_results(return_sorted=return_sorted)

    def is_early_stop_condition(self, i: int, early_stop: int) -> bool:
        if isinstance(early_stop, int) and i >= early_stop:
            references = self.client.get_trials_data_frame().tail(early_stop)[self.objectives[0]].to_numpy()
            early_stop_reference = references[0]
            recent_trial_best = references[1:].min()
            if early_stop_reference <= recent_trial_best:
                logger.info("Early stopped")
                return True
        return False

    def attach_custom_trial(self, parameters) -> pd.DataFrame:
        parameterization, trial_index = self.client.attach_trial(parameters=parameters)
        self.client.complete_trial(trial_index=trial_index, raw_data=self.evaluate(parameterization))
        return self.client.get_trials_data_frame().tail(1)

    def show_results(self, return_sorted: bool = False) -> pd.DataFrame:
        results = self.client.get_trials_data_frame().drop(columns=["arm_name", "trial_status"]).dropna()
        if return_sorted:
            return results.sort_values(by=self.objectives[0])
        else:
            return results

    def get_best(self) -> dict[str, float]:
        return self.client.get_best_parameters()
