from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):

    return {
        "status": "ok"
    }
