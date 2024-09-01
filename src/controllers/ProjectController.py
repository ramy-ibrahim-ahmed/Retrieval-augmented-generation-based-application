from .BaseController import BaseController
import os


# Project controller:
class ProjectController(BaseController):
    def __init__(self) -> None:
        super().__init__()

    # Makr project directory src/assets/files/project_id:
    def get_project_path(self, project_id: str):
        project_dir = os.path.join(self.file_dir, project_id)

        # Create directory if not exist:
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

        return project_dir
