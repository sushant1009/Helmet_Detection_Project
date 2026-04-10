from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as rest_router
from api.websocket import router as ws_router
from api.dependencies import set_yolo_model
from model_loader import load_model

app = FastAPI(title="Helmet Monitoring Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rest_router)
app.include_router(ws_router)


@app.on_event("startup")
def startup_event() -> None:
    model, device = load_model()
    set_yolo_model(model)
    print(f"[Startup] YOLO model loaded on device: {device}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=False)