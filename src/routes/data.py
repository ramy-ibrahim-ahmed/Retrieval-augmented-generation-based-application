from fastapi import APIRouter, UploadFile, status
from fastapi.responses import JSONResponse
from controllers import DataController, ProcessController
from .schemas.data import ProcessRequest
from models import ResponseSignal

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)


@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile):
    # Controllers
    data_controller = DataController()

    # Check file validation
    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": result_signal},
        )

    # Get file path to upload
    file_path, file_id = data_controller.generate_unique_filepath(
        original_filename=file.filename,
        project_id=project_id,
    )

    # Upload file
    is_uploaded, result_signal = await data_controller.upload_file(
        file=file, file_path=file_path
    )

    if not is_uploaded:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": result_signal},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": result_signal,
            "file_id": file_id,
        },
    )


@data_router.post("/process/{project_id}")
async def process_endpoint(project_id: str, process_request: ProcessRequest):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    chunk_overlap = process_request.chunk_overlap

    process_controller = ProcessController(project_id=project_id)

    file_content = process_controller.get_file_content(file_id=file_id)
    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROCESSING_FAILD.value,
            },
        )
    return file_chunks
