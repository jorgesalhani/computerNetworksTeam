import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

@router.get("/", response_class=FileResponse)
async def index():
    html_file_path = os.path.join(CURRENT_DIR, "home.html")
    if not os.path.exists(html_file_path):
        raise HTTPException(status_code=404, detail="home.html file not found")
        
    return FileResponse(html_file_path)