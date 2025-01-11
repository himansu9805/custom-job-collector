""" Models for the custom job collector app. """

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Job(BaseModel):
    """Job model."""

    title: str
    company: str
    location: str
    link: str
    posted_date: Optional[datetime] = None
