import joblib
import pandas as pd
from typing import Dict, Any

from app.config import (
    MODEL_PATH,
    SCALER_PATH,
    CATEGORICAL_ENCODER_PATH,
    FEATURE_COLUMNS_PATH,
    NUMERIC_FEATURES_PATH,
    CATEGORICAL_FEATURES_PATH,
    MODEL_METADATA_PATH,
)
from app.utils import get_logger, validate_numeric_ranges, InputValidationError, build_confidence_range, normalize_yes_no

logger = get_logger(__name__)

YES_NO_FIELDS = {"lift", "garden"}


class HousePricePredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.categorical_encoder = None
        self.feature_columns = None
        self.numeric_features = None
        self.categorical_features = None
        self.metadata = None
        self._loaded = False
        self._known_values_lower = {}

    def load(self) -> None:
        try:
            logger.info("Loading model artifacts...")

            required_paths = {
                "model": MODEL_PATH,
                "scaler": SCALER_PATH,
                "categorical_encoder": CATEGORICAL_ENCODER_PATH,
                "feature_columns": FEATURE_COLUMNS_PATH,
                "numeric_features": NUMERIC_FEATURES_PATH,
                "categorical_features": CATEGORICAL_FEATURES_PATH,
                "model_metadata": MODEL_METADATA_PATH,
            }
            for name, path in required_paths.items():
                if not path.exists():
                    raise FileNotFoundError(f"{name} file not found: {path}")

            self.model = joblib.load(MODEL_PATH)
            self.scaler = joblib.load(SCALER_PATH)
            self.categorical_encoder = joblib.load(CATEGORICAL_ENCODER_PATH)
            self.feature_columns = joblib.load(FEATURE_COLUMNS_PATH)
            self.numeric_features = joblib.load(NUMERIC_FEATURES_PATH)
            self.categorical_features = joblib.load(CATEGORICAL_FEATURES_PATH)
            self.metadata = joblib.load(MODEL_METADATA_PATH)

            self._known_values_lower = {
                "city": {v.lower(): v for v in self.metadata.get("known_cities", [])},
                "property_type": {v.lower(): v for v in self.metadata.get("known_property_types", [])},
                "facing": {v.lower(): v for v in self.metadata.get("known_facing", [])},
                "furnishing": {v.lower(): v for v in self.metadata.get("known_furnishing", [])},
                "lift": {v.lower(): v for v in self.metadata.get("known_lift", [])},
                "garden": {v.lower(): v for v in self.metadata.get("known_garden", [])},
            }

            self._loaded = True
            logger.info(f"Artifacts loaded successfully. Model: {self.metadata.get('model_name')}")

        except Exception as e:
            logger.error(f"Failed to load model artifacts: {str(e)}")
            self._loaded = False
            raise

    def is_ready(self) -> bool:
        return self._loaded

    def _resolve_categorical(self, field: str, value: str) -> str:
        v = value.strip()
        if field in YES_NO_FIELDS:
            v = normalize_yes_no(v)

        known_map = self._known_values_lower.get(field, {})
        if v.lower() in known_map:
            return known_map[v.lower()]
        return v

    def _build_feature_vector(self, data: Dict[str, Any]) -> pd.DataFrame:
        resolved_categorical = {
            field: self._resolve_categorical(field, data[field])
            for field in self.categorical_features
        }
        categorical_df = pd.DataFrame([resolved_categorical])[self.categorical_features]
        categorical_encoded = self.categorical_encoder.transform(categorical_df)
        categorical_encoded_cols = self.categorical_encoder.get_feature_names_out(self.categorical_features)
        categorical_encoded_df = pd.DataFrame(categorical_encoded, columns=categorical_encoded_cols)

        numeric_values = {field: [data[field]] for field in self.numeric_features}
        numeric_df = pd.DataFrame(numeric_values)[self.numeric_features]
        numeric_scaled = self.scaler.transform(numeric_df)
        numeric_scaled_df = pd.DataFrame(numeric_scaled, columns=self.numeric_features)

        combined = pd.concat([numeric_scaled_df, categorical_encoded_df], axis=1)

        for col in self.feature_columns:
            if col not in combined.columns:
                combined[col] = 0.0

        combined = combined[self.feature_columns]
        return combined

    def predict(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self._loaded:
            raise RuntimeError("Model artifacts are not loaded. Call load() first.")

        numeric_payload = {
            "bedrooms": request_data["bedrooms"],
            "bathrooms": request_data["bathrooms"],
            "sqft_living": request_data["sqft_living"],
            "sqft_lot": request_data["sqft_lot"],
            "floors": request_data["floors"],
            "parking": request_data["parking"],
            "nearby_schools": request_data["nearby_schools"],
            "nearby_hospitals": request_data["nearby_hospitals"],
            "balcony": request_data["balcony"],
            "age_of_property": request_data["age_of_property"],
        }
        validate_numeric_ranges(numeric_payload)

        model_input = dict(request_data)
        model_input["is_renovated"] = int(bool(request_data.get("is_renovated", False)))

        feature_vector = self._build_feature_vector(model_input)

        prediction_lakhs = float(self.model.predict(feature_vector)[0])
        prediction_lakhs = max(0.0, round(prediction_lakhs, 2))

        mape = self.metadata.get("mape", 10.0)
        confidence_range = build_confidence_range(prediction_lakhs, mape)

        return {
            "predicted_price_lakhs": prediction_lakhs,
            "predicted_price_rupees": round(prediction_lakhs * 100000, 2),
            "confidence_range_lakhs": confidence_range,
            "model_used": self.metadata.get("model_name", "unknown"),
        }

    def get_metadata_options(self) -> Dict[str, Any]:
        if not self._loaded:
            raise RuntimeError("Model artifacts are not loaded.")
        return {
            "cities": self.metadata.get("known_cities", []),
            "property_types": self.metadata.get("known_property_types", []),
            "facing_options": self.metadata.get("known_facing", []),
            "furnishing_options": self.metadata.get("known_furnishing", []),
            "lift_options": self.metadata.get("known_lift", []),
            "garden_options": self.metadata.get("known_garden", []),
        }

    def get_model_info(self) -> Dict[str, Any]:
        if not self._loaded:
            raise RuntimeError("Model artifacts are not loaded.")
        return {
            "model_name": self.metadata.get("model_name"),
            "rmse": self.metadata.get("rmse"),
            "mae": self.metadata.get("mae"),
            "r2": self.metadata.get("r2"),
            "mape": self.metadata.get("mape"),
            "cv_r2_mean": self.metadata.get("cv_r2_mean"),
            "cv_r2_std": self.metadata.get("cv_r2_std"),
            "total_feature_count": self.metadata.get("total_feature_count"),
        }


predictor = HousePricePredictor()