from enum import Enum


# Response signals:
class ResponseSignal(Enum):
    FILE_TYPE_NOT_SUPPORTED = "file type not supported!"
    FILE_TYPE_EXCEEDED = "file size exceeded!"
    Valid_FILE = "valid file!"
    FILE_UPLOADED = "file uploaded sucessfully!"
    FILE_FAILED_UPLOADED = "file failed upload!"
    PROCESSING_FAILD = "processing faild!"
    PROCESSING_SUCESS = "processing sucess!"
    FILES_NOT_FOUND = "files not found for project!"
    FILE_NOT_FOUND = "file not found for project!"
    FILE_ID_NOT_FOUND = "file ID needed!"
    FILE_ID_NOT_NEEDED = "field file ID not accepted!"
    FILE_LOADING_FAILD = "file loading failed!"
