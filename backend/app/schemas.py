from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class PredictionRequest(BaseModel):
    city: str = Field(..., description="Property city/location")
    property_type: str = Field(..., description="Type of property (e.g. Apartment, Villa)")
    facing: str = Field(..., description="Direction the property faces")
    furnishing: str = Field(..., description="Furnishing status")
    lift: str = Field(..., description="Lift availability (Yes/No)")
    garden: str = Field(..., description="Garden availability (Yes/No)")

    bedrooms: int = Field(..., ge=1, description="Number of bedrooms")
    bathrooms: int = Field(..., ge=1, description="Number of bathrooms")
    sqft_living: float = Field(..., gt=0, description="Living area in square feet")
    sqft_lot: float = Field(..., ge=0, description="Lot size in square feet")
    floors: int = Field(..., ge=1, description="Number of floors")
    parking: int = Field(..., ge=0, description="Number of parking spaces")
    nearby_schools: int = Field(..., ge=0, description="Number of nearby schools")
    nearby_hospitals: int = Field(..., ge=0, description="Number of nearby hospitals")
    balcony: int = Field(..., ge=0, description="Number of balconies")
    age_of_property: int = Field(..., ge=0, description="Age of property in years")
    is_renovated: bool = Field(default=False, description="Whether the property has been renovated")

    @field_validator("city", "property_type", "facing", "furnishing", "lift", "garden")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("field must not be empty")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "city": "Mumbai",
                "property_type": "Apartment",
                "facing": "North",
                "furnishing": "Semi-Furnished",
                "lift": "Yes",
                "garden": "No",
                "bedrooms": 3,
                "bathrooms": 2,
                "sqft_living": 1400.0,
                "sqft_lot": 2000.0,
                "floors": 10,
                "parking": 1,
                "nearby_schools": 3,
                "nearby_hospitals": 2,
                "balcony": 2,
                "age_of_property": 5,
                "is_renovated": False,
            }
        }


class PredictionResponse(BaseModel):
    predicted_price_lakhs: float
    predicted_price_rupees: float
    confidence_range_lakhs: List[float]
    model_used: str
    input_echo: PredictionRequest


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: Optional[str] = None


class MetadataResponse(BaseModel):
    cities: List[str]
    property_types: List[str]
    facing_options: List[str]
    furnishing_options: List[str]
    lift_options: List[str]
    garden_options: List[str]


class ModelInfoResponse(BaseModel):
    model_name: str
    rmse: float
    mae: float
    r2: float
    mape: float
    cv_r2_mean: float
    cv_r2_std: float
    total_feature_count: int


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None