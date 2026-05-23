from pydantic import BaseModel

class QrScanResponse(BaseModel):
    status: str
    qr_found: bool
    data: str