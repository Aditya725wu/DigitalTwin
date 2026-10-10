from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


SignalName = Literal["heart_rate", "hrv", "systolic_bp", "diastolic_bp", "spo2", "activity"]


class ReadingInput(BaseModel):
    timestamp: datetime | None = None
    heart_rate: float | None = Field(default=None, ge=25, le=240)
    hrv: float | None = Field(default=None, ge=1, le=250)
    systolic_bp: float | None = Field(default=None, ge=50, le=280)
    diastolic_bp: float | None = Field(default=None, ge=30, le=180)
    spo2: float | None = Field(default=None, ge=50, le=100)
    activity: float | None = Field(default=None, ge=0, le=100000)


class SimulateRequest(BaseModel):
    scenario: Literal["normal", "sustained_deviation", "recovery", "incomplete"] = "normal"
    hours: int = Field(default=1, ge=1, le=48)


class WhatIfRequest(BaseModel):
    changes: dict[SignalName, float | None]


class FamilyContactInput(BaseModel):
    authorized: bool
    name: str = "Family contact"
    fcm_token: str | None = None
