import logging
import sys
from app.config import (
    MIN_SQFT_LIVING, MAX_SQFT_LIVING,
    MIN_SQFT_LOT, MAX_SQFT_LOT,
    MIN_BEDROOMS, MAX_BEDROOMS,
    MIN_BATHROOMS, MAX_BATHROOMS,
    MIN_FLOORS, MAX_FLOORS,
    MIN_PARKING, MAX_PARKING,
    MIN_NEARBY_SCHOOLS, MAX_NEARBY_SCHOOLS,
    MIN_NEARBY_HOSPITALS, MAX_NEARBY_HOSPITALS,
    MIN_BALCONY, MAX_BALCONY,
    MIN_AGE_OF_PROPERTY, MAX_AGE_OF_PROPERTY,
)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


class InputValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def _check_range(value, min_v, max_v, field_name):
    if not (min_v <= value <= max_v):
        raise InputValidationError(f"{field_name} must be between {min_v} and {max_v}")


def validate_numeric_ranges(data: dict) -> None:
    _check_range(data["sqft_living"], MIN_SQFT_LIVING, MAX_SQFT_LIVING, "sqft_living")
    _check_range(data["sqft_lot"], MIN_SQFT_LOT, MAX_SQFT_LOT, "sqft_lot")
    _check_range(data["bedrooms"], MIN_BEDROOMS, MAX_BEDROOMS, "bedrooms")
    _check_range(data["bathrooms"], MIN_BATHROOMS, MAX_BATHROOMS, "bathrooms")
    _check_range(data["floors"], MIN_FLOORS, MAX_FLOORS, "floors")
    _check_range(data["parking"], MIN_PARKING, MAX_PARKING, "parking")
    _check_range(data["nearby_schools"], MIN_NEARBY_SCHOOLS, MAX_NEARBY_SCHOOLS, "nearby_schools")
    _check_range(data["nearby_hospitals"], MIN_NEARBY_HOSPITALS, MAX_NEARBY_HOSPITALS, "nearby_hospitals")
    _check_range(data["balcony"], MIN_BALCONY, MAX_BALCONY, "balcony")
    _check_range(data["age_of_property"], MIN_AGE_OF_PROPERTY, MAX_AGE_OF_PROPERTY, "age_of_property")

    if data["bathrooms"] > data["bedrooms"] + 2:
        raise InputValidationError("bathrooms is unrealistic relative to bedrooms (must be <= bedrooms + 2)")

    if data["sqft_living"] / max(data["bedrooms"], 1) < 250:
        raise InputValidationError("sqft_living is too low relative to bedrooms")


def normalize_category_string(value: str) -> str:
    return value.strip()


def normalize_yes_no(value: str) -> str:
    v = value.strip().lower()
    if v in ("yes", "y", "true", "1"):
        return "yes"
    if v in ("no", "n", "false", "0"):
        return "no"
    return v


def lakhs_to_rupees(price_lakhs: float) -> float:
    return round(price_lakhs * 100000, 2)


def build_confidence_range(predicted_price: float, mape_percent: float) -> list:
    margin = predicted_price * (mape_percent / 100)
    lower = round(max(0, predicted_price - margin), 2)
    upper = round(predicted_price + margin, 2)
    return [lower, upper]