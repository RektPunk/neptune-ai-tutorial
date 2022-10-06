from typing import Any, Dict, List, Union, Optional
import neptune.new as neptune
from module.project import NeptuneProjectManager
from module.experiment import NeptuneExperimentManager


class NeptuneModelStorageManager:
    def __init__(
        self,
        project_manager: NeptuneProjectManager,
        experiment_manager: Optional[NeptuneExperimentManager],
        key: str,
        **kwargs,
    ) -> None:
        """
        Neptune model storage manager\\
        manage models in f"{workspace_name}/{project_name}"

        Args:
            project_manager (NeptuneProjectManager)
            experiment_manager (Optional[NeptuneExperimentManager])
            key: model storage key, f"{project_name}-{key}"

        Methods:
            get_models()
            log_models_info()
            models_tags()
            log_model_info()
            log_run_info()
            model_tags()
            stop()
        """
        self._model_storage_key = key.upper()
        self._project_key = project_manager.get_key()
        self._project_name = project_manager.get_project_name()
        self._run_info = (
            experiment_manager.get_run_info() if experiment_manager else None
        )

        try:
            self.models = neptune.init_model(
                key=self._model_storage_key,
                project=self._project_name,
                api_token=project_manager.neptune_api_token,
                **kwargs,
            )
        except:
            self.models = neptune.init_model(
                with_id=f"{self._project_key}-{self._model_storage_key}",
                project=self._project_name,
                api_token=project_manager.neptune_api_token,
                **kwargs,
            )
        finally:
            self._models_url = self.models.get_url()

        self.model = neptune.init_model_version(
            with_id=f"{self._project_key}-{self._model_storage_key}",
            project=self._project_name,
            api_token=project_manager.neptune_api_token,
            **kwargs,
        )
        self._model_url = self.model.get_url()

    def get_models(self) -> List:
        """
        Get exist models in model storage
        Returns:
            List: _description_
        """
        _models = self.models.fetch_model_versions_table()
        return _models.to_rows()

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

    def stop(self) -> None:
        """
        End logging and sync
        """
        self.models.stop()
        self.model.stop()
