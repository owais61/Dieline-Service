from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import APP_NAME, ALLOWED_ORIGINS
from app.routers import dieline

app = FastAPI(title=APP_NAME)

# CORS is required since the .NET frontend runs on a different origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dieline.router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": APP_NAME}
