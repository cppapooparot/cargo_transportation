from fastapi import FastAPI

app = FastAPI(title="Cargo Transportation API")

@app.get("/health")
def health():
    return {"status": "ok"}