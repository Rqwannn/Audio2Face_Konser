from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from http import HTTPStatus
import json
from typing import List
from service.audio2face import Audio2FaceService
from utils.parsing_response import json_response, fail_response

router = APIRouter(prefix="/api/v1/face_generate")