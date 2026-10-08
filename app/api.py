from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Query

from app.client import UrjaClient
from app.models import (
    ConsumptionResponse,
    EnergyResponse,
    HealthResponse,
    LocationResponse,
    MeterListResponse,
)


app = FastAPI(
    title="Urja Meter API",
    description="A clean API service over the Urja Meter Ops portal.",
    version="1.0.0",
)


client = UrjaClient()


def ensure_login():
    if not client.session_established():
        try:
            client.login()
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail="Unable to authenticate with the Urja portal.",
            ) from exc


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
)
def health_check():
    return {"status": "ok"}


# --------------------------------------------------
# List Meters
# --------------------------------------------------

@app.get(
    "/meters",
    response_model=MeterListResponse,
    summary="List Meters",
)
def list_meters(
    q: str = Query(
        default="",
        description="Search query for meters",
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="Page number",
    ),
) -> dict[str, Any]:

    ensure_login()

    try:
        result = client.search_meters(
            query=q,
            page=page,
        )

        meters = []

        for meter in result.get("data", []):
            meters.append(
                {
                    "meter_id": meter.get("meterId"),
                    "serial_no": meter.get("serialNo"),
                    "make": meter.get("make"),
                    "phase_type": meter.get("phaseType"),
                    "install_status": meter.get("installStatus"),
                    "dt_code": meter.get("dtCode"),
                }
            )

        return {
            "meters": meters,
            "total": result.get("total", 0),
            "page": result.get("page", page),
            "page_size": result.get(
                "pageSize",
                len(meters),
            ),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch meters from the Urja portal.",
        ) from exc


# --------------------------------------------------
# Meter Energy
# --------------------------------------------------

@app.get(
    "/meters/{meter_id}/energy",
    response_model=EnergyResponse,
    summary="Get Meter Energy",
)
def get_meter_energy(meter_id: str):

    ensure_login()

    try:
        result = client.get_meter_energy(meter_id)

        readings = []

        for reading in result.get("data", []):
            readings.append(
                {
                    "timestamp": reading.get("timestamp"),
                    "kwh": (
                        float(reading["kwh"])
                        if reading.get("kwh") is not None
                        else None
                    ),
                    "kvarh": (
                        float(reading["kvarh"])
                        if reading.get("kvarh") is not None
                        else None
                    ),
                    "volt_r": (
                        float(reading["voltR"])
                        if reading.get("voltR") is not None
                        else None
                    ),
                }
            )

        return {
            "meter_id": meter_id,
            "readings": readings,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to fetch energy data for meter {meter_id}.",
        ) from exc


# --------------------------------------------------
# Meter Consumption
# --------------------------------------------------

@app.get(
    "/meters/{meter_id}/consumption",
    response_model=ConsumptionResponse,
    summary="Get Meter Consumption",
)
def get_meter_consumption(meter_id: str):

    ensure_login()

    try:
        result = client.get_meter_energy(meter_id)

        raw_readings = result.get("data", [])

        readings = []

        for reading in raw_readings:
            if reading.get("kwh") is None:
                continue

            timestamp = reading.get("timestamp")

            if not timestamp:
                continue

            readings.append(
                {
                    "timestamp": timestamp,
                    "kwh": float(reading["kwh"]),
                }
            )

        # Not enough readings to calculate consumption
        if len(readings) < 2:
            return {
                "meter_id": meter_id,
                "readings": [],
                "total_consumption_kwh": 0.0,
            }

        # Sort chronologically
        readings.sort(
            key=lambda x: datetime.strptime(
                x["timestamp"],
                "%d/%m/%Y %H:%M",
            )
        )

        consumption_readings = []
        total_consumption = 0.0

        for i in range(1, len(readings)):

            previous_kwh = readings[i - 1]["kwh"]
            current_kwh = readings[i]["kwh"]

            consumption = current_kwh - previous_kwh

            # Ignore negative differences caused by
            # meter reset or abnormal data.
            if consumption < 0:
                continue

            consumption = round(consumption, 4)

            consumption_readings.append(
                {
                    "timestamp": readings[i]["timestamp"],
                    "consumption_kwh": consumption,
                }
            )

            total_consumption += consumption

        return {
            "meter_id": meter_id,
            "readings": consumption_readings,
            "total_consumption_kwh": round(
                total_consumption,
                4,
            ),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to calculate consumption for meter {meter_id}.",
        ) from exc


# --------------------------------------------------
# Meter Location
# --------------------------------------------------

@app.get(
    "/meters/{meter_id}/location",
    response_model=LocationResponse,
    summary="Get Meter Location",
)
def get_meter_location(meter_id: str):

    ensure_login()

    try:
        result = client.get_meter_geo(meter_id)

        location = result.get("data")

        if location:
            location = {
                "latitude": float(location["latitude"]),
                "longitude": float(location["longitude"]),
            }

        return {
            "meter_id": meter_id,
            "location": location,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to fetch location for meter {meter_id}.",
        ) from exc