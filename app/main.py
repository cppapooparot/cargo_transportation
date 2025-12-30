from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(title="Cargo Transportation API")
app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok"}