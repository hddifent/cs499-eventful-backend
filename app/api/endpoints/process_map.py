from fastapi import APIRouter, UploadFile, File, HTTPException, status
import numpy as np
import cv2

from typing import Annotated

from app.services.image_processing import get_booths_from_map

router = APIRouter()

@router.post("/process")
async def detect_booth(file: Annotated[UploadFile, File(...)]):
    if ((file.content_type == None) or (not file.content_type.startswith("image/"))):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type"
        )
    
    file_contents = await file.read()
    np_image = np.frombuffer(file_contents, np.uint8)
    cv2_image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

    if cv2_image is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image failed to decode"
        )
    
    results = get_booths_from_map(cv2_image)

    return results