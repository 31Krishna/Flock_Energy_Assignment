from typing import Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class Meter(BaseModel):
    meter_id: Optional[str] = None
    serial_no: Optional[str] = None
    make: Optional[str] = None
    phase_type: Optional[str] = None
    install_status: Optional[str] = None
    dt_code: Optional[str] = None


class MeterListResponse(BaseModel):
    meters: list[Meter] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 0


class EnergyReading(BaseModel):
    timestamp: Optional[str] = None
    kwh: Optional[float] = None
    kvarh: Optional[float] = None
    volt_r: Optional[float] = None


class EnergyResponse(BaseModel):
    meter_id: str
    readings: list[EnergyReading] = Field(default_factory=list)


class ConsumptionReading(BaseModel):
    timestamp: Optional[str] = None
    consumption_kwh: Optional[float] = None


class ConsumptionResponse(BaseModel):
    meter_id: str
    readings: list[ConsumptionReading] = Field(default_factory=list)
    total_consumption_kwh: float = 0.0


class Location(BaseModel):
    latitude: float
    longitude: float


class LocationResponse(BaseModel):
    meter_id: str
    location: Optional[Location] = None