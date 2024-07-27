from enum import Enum


class ResponseSignal(Enum):
    FILE_TYPE_NOT_SUPPORTED = "file type not supported!"
    FILE_TYPE_EXCEEDED = "file size exceeded!"
    Valid_FILE = "valid file!"
    FILE_UPLOADED = "file uploaded sucessfully!"
    FILE_FAILED_UPLOADED = "file failed upload!"
