from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import APP_NAME, APP_VERSION, CORS_ORIGINS, BASE_DIR
from app.schemas import (
    PredictionRequest,
    PredictionResponse,
    HealthResponse,
    MetadataResponse,
    ModelInfoResponse,
)
from app.predictor import predictor
from app.utils import get_logger, InputValidationError

logger = get_logger(__name__)

FRONTEND_DIR = BASE_DIR.parent / "frontend"

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Production ML API for predicting house prices based on property features.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    try:
        predictor.load()
    except Exception as e:
        logger.error(f"Startup failed to load model: {str(e)}")


@app.get("/api", tags=["General"])
def api_root():
    return {
        "message": APP_NAME,
        "version": APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
def health_check():
    is_ready = predictor.is_ready()
    model_name = None
    if is_ready:
        try:
            model_name = predictor.metadata.get("model_name")
        except Exception:
            model_name = None
    return HealthResponse(
        status="healthy" if is_ready else "model_not_loaded",
        model_loaded=is_ready,
        model_name=model_name,
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict_price(request: PredictionRequest):
    if not predictor.is_ready():
        raise HTTPException(status_code=503, detail="Model is not loaded. Try again shortly.")

    try:
        result = predictor.predict(request.model_dump())
    except InputValidationError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal error while generating prediction.")

    return PredictionResponse(
        predicted_price_lakhs=result["predicted_price_lakhs"],
        predicted_price_rupees=result["predicted_price_rupees"],
        confidence_range_lakhs=result["confidence_range_lakhs"],
        model_used=result["model_used"],
        input_echo=request,
    )


@app.get("/metadata", response_model=MetadataResponse, tags=["Metadata"])
def get_metadata():
    if not predictor.is_ready():
        raise HTTPException(status_code=503, detail="Model is not loaded. Try again shortly.")

    try:
        options = predictor.get_metadata_options()
    except Exception as e:
        logger.error(f"Failed to fetch metadata: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve metadata.")

    return MetadataResponse(**options)


@app.get("/model-info", response_model=ModelInfoResponse, tags=["Metadata"])
def get_model_info():
    if not predictor.is_ready():
        raise HTTPException(status_code=503, detail="Model is not loaded. Try again shortly.")

    try:
        info = predictor.get_model_info()
    except Exception as e:
        logger.error(f"Failed to fetch model info: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve model info.")

    return ModelInfoResponse(**info)


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")