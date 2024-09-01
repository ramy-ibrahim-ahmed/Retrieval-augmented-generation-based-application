from fastapi import APIRouter, UploadFile, status, Request
from fastapi.responses import JSONResponse
from controllers import DataController, ProcessController
from .schemas import ProcessRequest
from models import ResponseSignal, ProjectModel, ChunkModel
from models.db_schemes import DataChunk

# Set router:
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)


### Upload files in a project ###
# when request attribute the function gets all request data include app data.
@data_router.post("/upload/{project_id}")
async def upload_data(
    request: Request,
    project_id: str,
    file: UploadFile,
):

    # Models:
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    # Controllers:
    data_controller = DataController()

    # Create or get project with the project id:
    project = await project_model.get_or_create_project(project_id=project_id)

    # Validate files to upload:
    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": result_signal},
        )

    # Get file path to upload:
    file_path, file_id = data_controller.generate_unique_filepath(
        original_filename=file.filename,
        project_id=project_id,
    )

    # Upload file:
    is_uploaded, result_signal = await data_controller.upload_file(
        file=file,
        file_path=file_path,
    )

    # Handle upload failing:
    if not is_uploaded:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": result_signal},
        )

    # Process succeeded:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": result_signal,
            "file_id": file_id,
        },
    )


### Chunk data project and insert on database ###
@data_router.post("/process/{project_id}")
async def process_endpoint(
    request: Request,
    project_id: str,
    process_request: ProcessRequest,
):

    # Get fileds request with validation:
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    chunk_overlap = process_request.chunk_overlap
    do_reset = process_request.do_reset

    # Models:
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    # Controllers:
    process_controller = ProcessController(project_id=project_id)

    # Get or Create project by ID:
    project = await project_model.get_or_create_project(project_id=project_id)

    # Process file in chunks
    # 1. Get file content.
    # 2. Get seperate content in chunks.
    file_content = process_controller.get_file_content(file_id=file_id)
    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    # Handle chunks failed:
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROCESSING_FAILD.value,
            },
        )

    # Convert chunks into DataChunk schema:
    file_chunks_records = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i + 1,
            chunk_project_id=project.id,
        )
        for i, chunk in enumerate(file_chunks)
    ]

    # If reset do remove the content project frome database first:
    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(project_id=project.id)

    # Insert chunks in database with bulk write:
    num_records = await chunk_model.insert_many_chunks(chunks=file_chunks_records)

    # Process succeeded:
    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCESS.value,
            "chunks inserted": num_records,
        }
    )
