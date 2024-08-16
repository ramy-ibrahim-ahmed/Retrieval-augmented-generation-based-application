import os
from .BaseController import BaseController
from .ProjectController import ProjectController
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models import ProcessingEnum


class ProcessController(BaseController):
    def __init__(self, project_id):
        """_summary_
        - use project ID to get project path from ProjectController.
        """
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)

    def get_file_extention(self, file_id: str):
        """_summary_
        - use file ID to get file extention as the last slice of str.
        - returns the file extention.
        """
        return os.path.splitext(file_id)[-1]

    def get_file_loader(self, file_id: str):
        """_summary_
        - get file ID to get file extension.
        - create file path using project path with file id.
        - if extention is supported return loader with path.
        - else None.
        """
        file_ext = self.get_file_extention(file_id=file_id)
        file_path = os.path.join(
            self.project_path,
            file_id,
        )
        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path=file_path, encoding="utf-8")
        if file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path=file_path)
        return None

    def get_file_content(self, file_id: str):
        """_summary_
        - take the file ID and get suit loader to get dile content.
        """
        loader = self.get_file_loader(file_id=file_id)
        return loader.load()

    def process_file_content(
        self,
        file_content: list,
        chunk_size: int = 100,
        chunk_overlap: int = 20,
    ):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        file_content_text = [rec.page_content for rec in file_content]
        file_content_metadata = [rec.metadata for rec in file_content]
        chunks = text_splitter.create_documents(
            texts=file_content_text,
            metadatas=file_content_metadata,
        )
        return chunks
