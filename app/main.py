from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import upload, ws, fetch

app = FastAPI(title="CaptionFlux API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # limit later
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(ws.router)
app.include_router(fetch.router)