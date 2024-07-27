import os
import random
import string
from helpers.config import get_settings, Settings


class BaseController:
    def __init__(self, app_settings: Settings = get_settings()) -> None:
        self.app_settings = app_settings
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.file_dir = os.path.join(self.base_dir, "assets/files")

        os.makedirs(self.file_dir, exist_ok=True)

    def generate_random_str(self, length: int = 12):
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
