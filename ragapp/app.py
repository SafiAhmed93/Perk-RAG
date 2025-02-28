from fastapi import FastAPI
from ragapp.models.models import ChatRequest
app = FastAPI()

@app.get("/auth")
def auth():
    
    return {"status": "success", "message": "Auth successful"}

@app.post("/chat/message")
def read_root(req: ChatRequest):
    return {
        "user": req.user,
        "message": req.message
    }