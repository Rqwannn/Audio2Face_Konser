# file: auth.py
import os
import httpx
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from typing import Dict, Any
from app.config import settings
from utils.parsing_response import json_response, fail_response

security_api_key = APIKeyHeader(name="x-api-key", auto_error=True)

async def verify_token_remote(api_key: HTTPAuthorizationCredentials = Depends(security_api_key)) -> Dict[str, Any]:
    """
    Dependency untuk memverifikasi token dengan menembak server lain.
    """
    headers = {
        "x-api-key": api_key, 
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                settings.AUTH_VERIFY_URL,
                headers=headers,
                timeout=5.0 
            )

            if response.status_code == 200:
                return response.json() 
            
            elif response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=fail_response(
                            "ENDPOINT_NOT_FOUND",
                            {
                                "status": 404,
                                "message": "Auth Server Not Found"
                            }
                        )
                    )
            else:
                data = response.json()
                data.pop("status", None)

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=fail_response(
                            "API_KEY_UNAUTHORIZED",
                            {
                                "status": 401,
                                "message": "API Key invalid or expired form Auth Server",
                                "response": data
                            }
                        )
                    )

        except httpx.RequestError as e:
            print(f"Auth Server Connection Error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=fail_response(
                    "SERVICE_UNAVAILABLE",
                    {
                        "status": 503,
                        "message": "Could not connect to Authentication Server"
                    }
                )
            )