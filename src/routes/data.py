from fastapi import APIRouter, UploadFile, status
from fastapi.responses import JSONResponse
from controllers import DataController

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
            "file_id":file_id,
        },
    )
