from fastapi import FastAPI

from api.routes import router

app = FastAPI(
    title="Lead Generation API",
    version="1.0.0"
)

app.include_router(router)


@app.get("/")
def health_check():
    return {
        "status": "running",
        "message": "Lead Generation API is up"
    }