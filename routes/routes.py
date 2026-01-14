from fastapi import APIRouter, Form, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from http import HTTPStatus
import json
import os
from typing import List
from service.audio2face import Audio2FaceService
from service.face_swapper import FaceSwapperService
from utils.parsing_response import json_response, fail_response
from utils.verify_token import verify_token_remote
from sqlalchemy.ext.asyncio import AsyncSession
from service.iris_data import DataDiriService
from service.object_storage import S3FileHandler

from app.config import get_db, settings

router = APIRouter(prefix="/api/v1/face_generate")

def get_service(db: AsyncSession = Depends(get_db)) -> DataDiriService:
    """Dependency untuk get service"""
    return DataDiriService(db)

swapper_service = FaceSwapperService(assets_dir="assets", use_gpu=True) 

@router.post("/change_face", status_code=HTTPStatus.CREATED)
async def enrollment_endpoint(
    nik: str = Form(..., description="National ID Number (unique)"),
    service: DataDiriService = Depends(get_service),
    user: dict = Depends(verify_token_remote)
):
    image_upload = None
    swapped_image_path = None 

    try:        
        file_wajah = await service.get_file_wajah_by_nik(nik)

        if file_wajah is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=fail_response(
                    "ENROLLMENT_FAILED",
                    {
                        "status": status.HTTP_404_NOT_FOUND,
                        "message":"Data tidak ditemukan"
                    }
                )
            )
        
        s3_handler = S3FileHandler(
            access_key=settings.ACCESS_KEY_BUCKET_PROD,
            secret_key=settings.PRIVATE_KEY_BUCKET_PROD,
            region=settings.REGION_BUCKET_PROD,
            bucket_name=settings.S3_BUCKET_PROD,
            endpoint_url=settings.SERVER_BUCKET_PROD
        )

        image_upload = await s3_handler.download_to_uploadfile(
            file_wajah,
            suffix='.jpg'
        )

        source_bytes = await image_upload.read()
        
        target_avatar_path = os.path.join("assets", "testing_man.jpeg") 
        output_filename = f"swapped_{nik}.jpg"
        temp_output_path = os.path.join("temp", output_filename)

        swapped_image_path = swapper_service.process_swap(
            source_bytes=source_bytes,
            target_path=target_avatar_path,
            output_path=temp_output_path
        )

        result = await Audio2FaceService.predict(
            image_path=swapped_image_path, 
        )

        response_payload = {
            "status": 200,
            "data": result
        }

        return json_response("ENROLLMENT_SUCCESS", response_payload), 201
        
    except HTTPException as http_exc:
        return JSONResponse(
            status_code=http_exc.status_code,
            content=http_exc.detail
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=fail_response(
                "ENROLLMENT_ERROR",
                {
                    "status": 500,
                    "message": f"Unexpected error: {str(e)}"
                }
            )
        )
    finally:
        if image_upload:
            await S3FileHandler.cleanup_uploadfile(image_upload)
        
        if swapped_image_path and os.path.exists(swapped_image_path):
            os.remove(swapped_image_path)