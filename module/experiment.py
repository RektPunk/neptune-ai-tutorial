import os
from typing import Any, Dict, List, Optional, Union
import neptune.new as neptune
from module.project import NeptuneProjectManager
from module.variables import NeptuneMode


class NeptuneExperimentManager:
    """
    Neptune experiment manager\\
    manage experiment in f"{workspace_name}/{project_name}"

    Args:
        project_manager (NeptuneProjectManager)
        mode (Optional[str]): neptune mode

    Methods:
        get_run_info()
        tags()
        log_value()
        log_series()
        upload()
        stop()
    """

    def __init__(
        self,
        project_manager: NeptuneProjectManager,
        mode: Optional[str] = NeptuneMode.ASYNC,
        **kwargs,
    ) -> None:
        """
        Args:
            project_manager (NeptuneProjectManager)
            mode (Optional[str]): neptune mode
        """
        self.run = neptune.init(
            project=project_manager.get_project_name(),
            api_token=project_manager.neptune_api_token,
            mode=mode,
            **kwargs,
        )
        self.project_manager = project_manager
        self.mode = mode
        self.run_url: str = self.run.get_run_url()
        self.run_id: str = self.run._sys_id

    def get_run_info(self) -> Dict[str, str]:
        """
        Get experiment status
        Returns:
            Dict[str, str]: {"id": run_id, "url": run_url}
        """
        return {
            "run_id": self.run_id,
            "run_url": self.run_url,
        }

    def tags(self, tags: Union[List[str], str]) -> None:
        """
        Add tags of experiment
        Args:
            tags (Union[List[str], str])
        """
        self.run["sys/tags"].add(tags)

    def log_value(self, name: str, params: Dict[str, Any]) -> None:
        """
        Logging single point of value
        Args:
            name (str): name of logging space such as "train" or "parameters"
            params (Dict[str, Any]): {"lr" : 0.001, "batch_size": 8}
        """
        self.run[name] = params

    def log_series(self, name: str, metric_name: str, metric_value: float) -> None:
        """
        Logging multiple points of value
        Args:
            name (str): name of logging space such as "train" or "test"
            metric_name (str): name of metric
            metric_value (float): value of metric
        """
        self.run[f"{name}/{metric_name}"].log(metric_value)

    def upload(self, name: str, path: Union[List[str], str]) -> None:
        """
        Upload files
        Args:
            name (str): name of logging space such as "train" or "test"
            path (Union[List[str], str]): file path
        """
        self.run[name].upload_files(path)

    def stop(self):
        """
        End logging and sync
        """
        if self.mode == NeptuneMode.OFFLINE:
            os.environ["NEPTUNE_PROJECT"] = self.project_manager()
            os.system("neptune sync")
        self.run.stop()
