from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.source.routers import qr_scan_router
from app.display import camera_web_ui

app = FastAPI(title="QR Code Reader API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(qr_scan_router.router)
app.include_router(camera_web_ui.router)