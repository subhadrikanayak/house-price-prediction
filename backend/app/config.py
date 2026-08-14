import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"

MODEL_PATH = MODELS_DIR / "best_model.joblib"
SCALER_PATH = MODELS_DIR / "scaler.joblib"
CATEGORICAL_ENCODER_PATH = MODELS_DIR / "categorical_encoder.joblib"
FEATURE_COLUMNS_PATH = MODELS_DIR / "feature_columns.joblib"
NUMERIC_FEATURES_PATH = MODELS_DIR / "numeric_features.joblib"
CATEGORICAL_FEATURES_PATH = MODELS_DIR / "categorical_features.joblib"
MODEL_METADATA_PATH = MODELS_DIR / "model_metadata.joblib"

APP_NAME = "House Price Prediction API"
APP_VERSION = "2.0.0"

CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "*",
]

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
RELOAD = os.getenv("RELOAD", "true").lower() == "true"

MIN_SQFT_LIVING = 100.0
MAX_SQFT_LIVING = 30000.0
MIN_SQFT_LOT = 0.0
MAX_SQFT_LOT = 100000.0
MIN_BEDROOMS = 1
MAX_BEDROOMS = 20
MIN_BATHROOMS = 1
MAX_BATHROOMS = 20
MIN_FLOORS = 1
MAX_FLOORS = 100
MIN_PARKING = 0
MAX_PARKING = 10
MIN_NEARBY_SCHOOLS = 0
MAX_NEARBY_SCHOOLS = 50
MIN_NEARBY_HOSPITALS = 0
MAX_NEARBY_HOSPITALS = 50
MIN_BALCONY = 0
MAX_BALCONY = 10
MIN_AGE_OF_PROPERTY = 0
MAX_AGE_OF_PROPERTY = 100