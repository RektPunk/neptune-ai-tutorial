import os
from neptune import management
from module.credential import NeptuneToken


class NeptuneProjectManager(NeptuneToken):
    """
    Neptune project manager\\
    Create or delete project named f"{workspace_name}/{projectname}"

    Args:
        workspace_name (str): workspace name
        project_name (str): project name
        key (str): key of f"{workspace_name}/{projectname}"

    Methods:
        create()
        delete()
    """

    def __init__(
        self,
        workspace_name: str,
        project_name: str,
        key: str,
    ) -> None:
        """
        Args:
            workspace_name (str): workspace name
            project_name (str): project name
            key (str): key of f"{workspace_name}/{projectname}"
        """
        super().__init__()
        self.project_full_name = f"{workspace_name}/{project_name}"
        self.key = key

    def __call__(self):
        return self.project_full_name

    def create(self) -> None:
        """
        Create project f"{workspace_name}/{projectname}"
        """
        _projects = management.get_project_list()
        if self.project_full_name not in _projects:
            management.create_project(
                name=self.project_full_name,
                key=self.key,
                api_token=self.neptune_api_token,
            )

    def delete(self) -> None:
        """
        Delete project f"{workspace_name}/{projectname}"
        """
        _projects = management.get_project_list()
        if self.project_full_name in _projects:
            management.delete_project(
                name=self.project_full_name,
                api_token=self.neptune_api_token,
            )