from helpers import get_settings


class BaseDataModel:
    # pass db_client for database processes.
    # pass settings.
    def __init__(self, db_client: object):
        self.db_client = db_client
        self.app_settings = get_settings()
