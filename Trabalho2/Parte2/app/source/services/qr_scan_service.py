from fastapi import UploadFile, HTTPException
from PIL import Image
from pyzbar.pyzbar import decode
import io

from app.source.models.qr_scan_model import QrScanResponse

class QrScanService:
    async def scan(self, file: UploadFile):
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File provided is not an image.")
        
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        decoded_objects = decode(image)
        
        if not decoded_objects:
            return QrScanResponse(
                status='success',
                qr_found=False,
                data=None
            )
        
        qr_data = decoded_objects[0].data.decode("utf-8")
        
        return QrScanResponse(
            status='success',
            qr_found=True,
            data=qr_data
        )
    