import os
from .BaseController import BaseController
from .ProjectController import ProjectController
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models.enums import ProcessingEnum


# Process controller for chunk an uploaded file:
class ProcessController(BaseController):

    # Get project path:
    def __init__(self, project_id):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)

    # Get file extention as the last slice of str:
    def get_file_extention(self, file_id: str):
        return os.path.splitext(file_id)[-1]

    # Get file loader with path to load in:
    def get_file_loader(self, file_id: str):
        # 1. get file ID to get file extension.
        # 2. create file path using project path with file id.
        # 3. if extention is supported return loader with path.
        file_ext = self.get_file_extention(file_id=file_id)
        file_path = os.path.join(
            self.project_path,
            file_id,
        )
        if not os.path.exists(file_path):
            return None
        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path=file_path, encoding="utf-8")
        if file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path=file_path)
        return None

    # Get file content by loader:
    def get_file_content(self, file_id: str):
        loader = self.get_file_loader(file_id=file_id)
        if loader:
            return loader.load()
        else:
            return None

    # Seperate file to chunks:
    def process_file_content(
        self,
        file_content: list,
        chunk_size: int = 100,
        chunk_overlap: int = 20,
    ):

        # Split via chars:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

        # List text chunks and metadata chunks from splitter:
        file_content_text = [rec.page_content for rec in file_content]
        file_content_metadata = [rec.metadata for rec in file_content]

        # Create & Return chunks:
        chunks = text_splitter.create_documents(
            texts=file_content_text,
            metadatas=file_content_metadata,
        )
        return chunks
