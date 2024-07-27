from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
from models import ResponseSignal
import re
import os
import aiofiles
import logging

logger = logging.getLogger("data_upload.error")


class DataController(BaseController):
    def __init__(self) -> None:
        super().__init__()  # inherite from base controller
        self.size_scale = 1024 * 1024  # scale for convert from byte to mega-byte

    # file validation
    def validate_uploaded_file(self, file: UploadFile) -> bool:

        # check file type
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        # check file size
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_TYPE_EXCEEDED.value

        return True, ResponseSignal.Valid_FILE.value

    def get_clean_file_name(self, original_filename: str):
        clean_filename = re.sub(r"[^\w.]", "", original_filename.strip())
        clean_filename = clean_filename.replace(" ", "_")
        return clean_filename

    def generate_unique_filename(self, original_filename: str, project_id: str):
        project_path = ProjectController().get_project_path(project_id=project_id)
        random_perfix = self.generate_random_str()
        clean_filename = self.get_clean_file_name(original_filename=original_filename)
        new_file_path = os.path.join(project_path, random_perfix + "_" + clean_filename)

        while os.path.exists(new_file_path):
            random_perfix = self.generate_random_str()
            new_file_path = os.path.join(
                project_path, random_perfix + "_" + clean_filename
            )

        return new_file_path

    async def upload_file(self, file, file_path):
        try:
            async with aiofiles.open(file=file_path, mode="wb") as f:
                while chunk := await file.read(
                    self.app_settings.FILE_DEFAULT_CHUNK_SIZE
                ):
                    await f.write(chunk)

            return True, ResponseSignal.FILE_UPLOADED.value

        except Exception as e:
            logger.error(f"error while uploading file {file_path}: {e}")

            return False, ResponseSignal.FILE_FAILED_UPLOADED.value