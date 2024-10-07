import os
import logging
from fastapi import APIRouter, UploadFile, status, Request
from fastapi.responses import JSONResponse
from controllers import DataController, ProcessController
from .schemas import ProcessRequest
from models import ProjectModel, ChunkModel, AssetModel
from models.enums import ResponseSignal, AssetTypeEnum
from models.db_schemes import DataChunk, Asset

# Logger:
logger = logging.getLogger("uvicorn.error")

# Set router:
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)


##################################################################### Upload files in projects ###
# when request attribute the function gets all request data include app data.
@data_router.post("/upload/{project_id}")
async def upload_data(
    request: Request,
    project_id: str,
    file: UploadFile,
):

    # Models:
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)

    # Controllers:
    data_controller = DataController()

    # Get or create by project ID:
    project = await project_model.get_or_create_project(project_id=project_id)

    # File validation:
    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": result_signal},
        )

    # Generate project folder if not exist & Get path:
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

    # Create asset for project's files:
    asset_resource = Asset(
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path),
    )

    # Insert asset in Database:
    asset_record = await asset_model.create_asset(asset=asset_resource)

    # Process succeeded:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": result_signal,
            "uploaded at": str(asset_record.asset_pushed_at),
        },
    )


###################################################################### Process project's files ###
@data_router.post("/process/{project_id}")
async def process_endpoint(
    request: Request,
    project_id: str,
    process_request: ProcessRequest,
):
    # Validate request data:
    chunk_size = process_request.chunk_size
    chunk_overlap = process_request.chunk_overlap
    do_reset = process_request.do_reset

    # Manual form validation for file ID:
    if process_request.file_id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_ID_NOT_NEEDED.value,
            },
        )

    # Models:
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)

    # Controllers:
    process_controller = ProcessController(project_id=project_id)

    # Get or Create project by ID:
    project = await project_model.get_or_create_project(project_id=project_id)

    # If do reset remove the content project from database first:
    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(project_id=project.id)

    # Get all project's assets:
    project_files = await asset_model.get_all_project_assets(
        project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value,
    )

    # Get just assets IDs and assets names:
    project_files_ids = {record.id: record.asset_name for record in project_files}

    # Validate assets exist for the requested project:
    if len(project_files_ids) == 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignal.FILES_NOT_FOUND.value,
            },
        )

    # Process asset by asset:
    num_records = 0
    num_files = 0
    for asset_id, file_id in project_files_ids.items():

        # Get file content:
        file_content = process_controller.get_file_content(file_id=file_id)

        # Validate file exists & and continue:
        if file_content is None:
            logging.error(f"Error while processing: {file_id}")
            continue

        # Process file:
        file_chunks = process_controller.process_file_content(
            file_content=file_content,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        # Validate file processing:
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
                chunk_asset_id=asset_id,
            )
            for i, chunk in enumerate(file_chunks)
        ]

        # Insert chunks in Database with bulk write:
        num_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
        num_files += 1

    # Process succeeded:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.PROCESSING_SUCESS.value,
            "chunks inserted": num_records,
            "processed_files": num_files,
        },
    )


################################################################## Process one file in project ###
@data_router.post("/process_file/{project_id}")
async def process_file_endpoint(
    request: Request,
    project_id: str,
    process_request: ProcessRequest,
):
    # Validate request data:
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    chunk_overlap = process_request.chunk_overlap
    do_reset = process_request.do_reset

    # Manual form validation for file ID:
    if file_id is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_ID_NOT_FOUND.value,
            },
        )

    # Models:
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)

    # Controllers:
    process_controller = ProcessController(project_id=project_id)

    # Get or Create project by ID:
    project = await project_model.get_or_create_project(project_id=project_id)

    # If do reset remove the content project from database first:
    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(project_id=project.id)

    # Get asset:
    asset_record = await asset_model.get_asset_record(
        asset_project_id=project.id,
        asset_name=process_request.file_id,
    )

    # Validate asset exist:
    if asset_record is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignal.FILE_NOT_FOUND.value,
            },
        )

    # Get file content:
    file_content = process_controller.get_file_content(file_id=file_id)

    # Validate asset loading:
    if file_content is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_LOADING_FAILD.value,
            },
        )

    # File processing:
    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    # Validate file processing:
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
            chunk_asset_id=asset_record.id,
        )
        for i, chunk in enumerate(file_chunks)
    ]

    # Insert chunks in Database with bulk write:
    num_records = await chunk_model.insert_many_chunks(chunks=file_chunks_records)

    # Process succeeded:
    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCESS.value,
            "chunks inserted": num_records,
        }
    )
