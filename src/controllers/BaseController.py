import os
import random
import string
from helpers import get_settings, Settings


# Base controller:
# 1. settings
# 2. src directory
# 3. assets directory -> files subdirectory for base projects files
class BaseController:
    def __init__(self, app_settings: Settings = get_settings()) -> None:
        self.app_settings = app_settings
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.file_dir = os.path.join(self.base_dir, "assets/files")

        # Make files main durectory:
        os.makedirs(self.file_dir, exist_ok=True)

    # Generate random string from nums and chars:
    def generate_random_str(self, length: int = 12):
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
