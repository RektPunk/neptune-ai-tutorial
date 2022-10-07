from typing import Any, Dict, List, Union, Optional
import pandas as pd
import neptune.new as neptune
from module.project import NeptuneProjectManager
from module.experiment import NeptuneExperimentManager
from module.variables import NeptuneModelStage


class NeptuneModelStorageManager:
    """
    Neptune model storage manager\\
    manage models in f"{workspace_name}/{project_name}"

    Args:
        project_manager (NeptuneProjectManager)
        experiment_manager (Optional[NeptuneExperimentManager])
        key: model storage key, f"{project_name}-{key}"
        model_id: model id, f"{project_name}-{key}-{model_id}"

    Methods:
        get_models()
        log_models_info()
        models_tags()
        log_model_info()
        log_run_info()
        model_tags()
        change_stage()
        stop()
    """

    def __init__(
        self,
        project_manager: NeptuneProjectManager,
        experiment_manager: Optional[NeptuneExperimentManager],
        key: str,
        model_id: Optional[int] = None,
        **kwargs,
    ) -> None:
        """
        Args:
            project_manager (NeptuneProjectManager)
            experiment_manager (Optional[NeptuneExperimentManager])
            key: model storage key, f"{project_name}-{key}"
            model_id: model id, f"{project_name}-{key}-{model_id}"
        """
        self._model_storage_key = key.upper()
        self._project_key = project_manager.get_key()
        self._project_name = project_manager.get_project_name()
        self._neptune_api_token = project_manager.neptune_api_token
        self._run_info = (
            experiment_manager.get_run_info() if experiment_manager else None
        )

        try:
            self.models = neptune.init_model(
                key=self._model_storage_key,
                project=self._project_name,
                api_token=self._neptune_api_token,
                **kwargs,
            )
        except:
            self.models = neptune.init_model(
                with_id=f"{self._project_key}-{self._model_storage_key}",
                project=self._project_name,
                api_token=self._neptune_api_token,
                **kwargs,
            )
        finally:
            self._models_url = self.models.get_url()

        if model_id is not None:
            self._model_id = model_id
            self.model = neptune.init_model_version(
                with_id=f"{self._project_key}-{self._model_storage_key}-{self._model_id}",
                project=self._project_name,
                api_token=self._neptune_api_token,
                **kwargs,
            )
        else:
            self.model = neptune.init_model_version(
                model=f"{self._project_key}-{self._model_storage_key}",
                project=self._project_name,
                api_token=self._neptune_api_token,
                **kwargs,
            )
        self._model_url = self.model.get_url()

    def get_models(self) -> pd.DataFrame:
        """
        Get exist models in model storage
        Returns:
            pd.DataFrame
        """
        _models = self.models.fetch_model_versions_table()
        return _models.to_pandas()

    def log_models_info(self, name: str, params: Dict[str, Any]) -> None:
        """
        Logging single point of value
        Args:
            name (str): name of logging space such as "train" or "parameters"
            params (Dict[str, Any]): {"lr" : 0.001, "batch_size": 8}
        """
        self.models[name] = params

    def models_tags(self, tags: Union[List[str], str]) -> None:
        """
        Add tags of models
        Args:
            tags (Union[List[str], str])
        """
        self.models["sys/tags"].add(tags)

    def log_model_info(self, name: str, params: Dict[str, Any]) -> None:
        """
        Logging single point of value
        Args:
            name (str): name of logging space such as "train" or "parameters"
            params (Dict[str, Any]): {"lr" : 0.001, "batch_size": 8}
        """
        self.model[name] = params

    def log_run_info(self) -> None:
        """
        Logging run info in model
        """
        if self._run_info:
            self.model["run_info"] = self._run_info

    def model_tags(self, tags: Union[List[str], str]) -> None:
        """
        Add tags of model
        Args:
            tags (Union[List[str], str])
        """
        self.model["sys/tags"].add(tags)

    def change_stage(self, stage: str) -> None:
        """
        Change model stage
        Args:
            stage (str): stage name, one of [None, Production, Staging, Archived]
        """
        _stage = stage.upper()
        if _stage in NeptuneModelStage._member_names_:
            self.model.change_stage(NeptuneModelStage[_stage])

    def get_stage_model(self, stage: str, **kwargs) -> None:
        """
        Change model to latest model with stage
        Args:
            stage (str): stage name, one of [None, Production, Staging, Archived]
        """
        _stage = stage.upper()
        if _stage in NeptuneModelStage._member_names_:
            _models = self.get_models()
            _candidate_models = _models.loc[
                _models["sys/stage"] == NeptuneModelStage[_stage]
            ]
            if len(_candidate_models) != 0:
                _stage_model = _candidate_models.sort_values(
                    "sys/modification_time", ascending=False
                ).iloc[0]
                self.model.stop()
                self.model = neptune.init_model_version(
                    with_id=_stage_model["sys/id"],
                    project=self._project_name,
                    api_token=self._neptune_api_token,
                    **kwargs,
                )

    def stop(self) -> None:
        """
        End logging and sync
        """
        self.models.stop()
        self.model.stop()
