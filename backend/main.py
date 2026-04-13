from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.generate import router as generate_router
from routes.image import router as image_router

app = FastAPI(title="ChartGPT API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_router, prefix="/api/generate", tags=["Generate"])
app.include_router(image_router, prefix="/api/image", tags=["Image"])


@app.get("/")
def root():
    return {"status": "ChartGPT API is running"}
