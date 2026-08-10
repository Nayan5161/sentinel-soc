from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, ConfigDict


class Source(BaseModel):
    source_id: str
    source_type: str
    hostname: str | None = None
    ip: str | None = None


class Actor(BaseModel):
    ip: str | None = None
    user: str | None = None
    country: str | None = None


class Target(BaseModel):
    hostname: str | None = None
    ip: str | None = None
    resource: str | None = None
    port: int | None = None


class EventDetails(BaseModel):
    category: str
    action: str
    status: str = "unknown"
    severity: str = "info"
    message: str = ""


class Network(BaseModel):
    protocol: str | None = None
    direction: str | None = None
    port: int | None = None


class SecurityEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    event_id: str | None = None

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    source: Source
    actor: Actor = Field(default_factory=Actor)
    target: Target = Field(default_factory=Target)
    event: EventDetails
    network: Network = Field(default_factory=Network)

    detection: dict[str, Any] = Field(default_factory=dict)

    raw: dict[str, Any] = Field(default_factory=dict)
