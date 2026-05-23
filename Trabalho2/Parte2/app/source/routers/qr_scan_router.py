from fastapi import APIRouter, File, UploadFile, HTTPException

from app.source.services.qr_scan_service import QrScanService
from app.source.models.qr_scan_model import QrScanResponse
import traceback

router = APIRouter(prefix="/api/v1")

@router.post("/scan-qr", response_model=QrScanResponse)
async def scan_qr(file: UploadFile = File(...)):
    try:
        print(file, flush=True)
        qr_scan_service = QrScanService()
        return await qr_scan_service.scan(file=file)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing image: {str(e)}. Traceback: {traceback.format_exc()}"
        )
