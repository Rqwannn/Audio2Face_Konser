from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool
from dotenv import load_dotenv
import tempfile
import shutil
import os
import datetime
import time
from typing import Optional, Dict, Any, Literal, List

class Audio2FaceService:
    
    def __init__(self, vector_db_type: Literal["faiss", "pinecone"] = "faiss"):
        pass