from typing import Union
from pydantic import BaseModel


class ScrapeParamsModel(BaseModel):
    addMoreHostInfo: bool = False
    calendarMonths: int = 2
    checkIn: str
    checkOut: str
    currency: str = "USD"
    maxListings: int = 10
    includeReviews: bool = True
    maxReviews: int = 10
    locationQuery: str
    simple: bool = False
    timeoutMs: int = 60000
    limitPoints: int = 100
    debugLog: bool = False
    maxConcurrency: int = 50
