import os
import cv2
import numpy as np
from pathlib import Path
from fastapi import HTTPException, status
from utils.models.check_model import get_model
from utils.face_analysis import FaceAnalysis
from utils.parsing_response import fail_response

class FaceSwapperService:
    def __init__(self, assets_dir: str, use_gpu: bool = True):
        self.assets_dir = Path(assets_dir)
        self.model_path = self.assets_dir / 'inswapper_128.onnx'
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model swapper tidak ditemukan di: {self.model_path}")

        self.ctx_id = 0 if use_gpu else -1
        provider = ['CUDAExecutionProvider'] if use_gpu else ['CPUExecutionProvider']

        print(f"[INFO] Loading FaceAnalysis from {self.assets_dir}...")

        self.app = FaceAnalysis(name='buffalo_l', root=str(self.assets_dir))
        self.app.prepare(ctx_id=self.ctx_id, det_size=(640, 640))

        print("[INFO] Loading Inswapper Model...")
        self.swapper = get_model(
            str(self.model_path), 
            providers=provider
        )

    def process_swap(self, source_bytes: bytes, target_path: str, output_path: str):
        """
        source_bytes: Data gambar dari UploadFile (Front End)
        target_path: Path lokal foto target (Server)
        output_path: Path lokal untuk menyimpan hasil
        """
        
        if not os.path.exists(target_path):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=fail_response(
                    "SWAP_CONFIG_ERROR",
                    {
                        "status": 500,
                        "message": f"Target avatar image not found at: {target_path}"
                    }
                )
            )

        img_target = cv2.imread(target_path)

        nparr = np.frombuffer(source_bytes, np.uint8)
        img_source = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img_source is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=fail_response(
                    "INVALID_IMAGE_FILE",
                    {
                        "status": 400,
                        "message": "Gagal decode source image. File korup atau format tidak didukung."
                    }
                )
            )

        faces_source = self.app.get(img_source)
        faces_target = self.app.get(img_target)

        if not faces_source:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=fail_response(
                    "NO_FACE_DETECTED",
                    {
                        "status": 400,
                        "message": "Tidak ada wajah terdeteksi di foto yang diupload. Pastikan wajah terlihat jelas."
                    }
                )
            )

        if not faces_target:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=fail_response(
                    "TARGET_FACE_ERROR",
                    {
                        "status": 500,
                        "message": "Tidak ada wajah terdeteksi di foto Avatar Target (Server Asset)."
                    }
                )
            )

        try:
            source_face = faces_source[0]
            target_face = faces_target[0]

            res_img = self.swapper.get(img_target, target_face, source_face, paste_back=True)

            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            cv2.imwrite(output_path, res_img)
            
            return output_path

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=fail_response(
                    "SWAPPING_PROCESS_FAILED",
                    {
                        "status": 500,
                        "message": f"Terjadi kesalahan saat proses face swapping: {str(e)}"
                    }
                )
            )