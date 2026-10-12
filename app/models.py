from enum import StrEnum
from typing import Annotated, Literal, Self
from pydantic import BaseModel, Field, model_validator

class DeviceStatus(StrEnum):
    IN_SERVICE = "in_service"
    AVAILABLE = "available"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"
    STORAGE = "storage"
    RMA = "rma"
    DECOMMISSIONED = "decommissioned"


class DeviceCondition(StrEnum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    EMPTY_CHASSIS = "empty_chassis"


class PartCondition(StrEnum):
    NEW = "new"
    TESTED_GOOD = "tested_good"
    UNTESTED = "untested"
    FAILED = "failed"


class ComponentType(StrEnum):
    MOTHERBOARD = "motherboard"
    CPU = "cpu"
    DIMM = "dimm"
    NVME = "nvme"
    NIC = "nic"
    GPU = "gpu"
    FPGA = "fpga"
    ENCODER = "encoder"
    PSU = "psu"
    FAN = "fan"


class IpMode(StrEnum):
    STATIC = "static"
    DHCP_RESERVED = "dhcp_reserved"
    DHCP = "dhcp"


class IpPolicy(StrEnum):
    STABLE_REQUIRED = "stable_required"
    DYNAMIC_ALLOWED = "dynamic_allowed"


class UserRole(StrEnum):
    DEVELOPER = "developer"
    LAB_TECH = "lab_tech"
    LAB_ENGINEER = "lab_engineer"
    MANAGER = "manager"


class TicketSource(StrEnum):
    DETECTED = "detected"
    REPORTED = "reported"


class ReservationStatus(StrEnum):
    REQUESTED = "requested"
    ACTIVE = "active"
    EXTENDED = "extended"
    RETURNED = "returned"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class QualificationStatus(StrEnum):
    CANDIDATE = "candidate"
    TESTING = "testing"
    ON_HOLD = "on_hold"
    QUALIFIED = "qualified"
    REJECTED = "rejected"


class InboundStatus(StrEnum):
    ORDERED = "ordered"
    SHIPPED = "shipped"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class Disposition(StrEnum):
    INSTALL = "install"
    STAGE = "stage"
    STORAGE = "storage"
    SHIP_TO_USER = "ship_to_user"


class RackLocation(BaseModel):
    kind: Literal["rack"] = "rack"
    site_id: str
    rack_id: str
    rack_unit: int = Field(ge=1, le=60)
    height_u: int = Field(default=1, ge=1, le=10)


class StorageLocation(BaseModel):
    kind: Literal["storage"] = "storage"
    site_id: str
    room: str
    shelf: str
    bin: str | None = None


Location = Annotated[RackLocation | StorageLocation, Field(discriminator="kind")]


class PartModel(BaseModel):
    part_model_id: str
    component_type: ComponentType
    make: str
    model: str
    specs: dict[str, str | int | float] = {}


class Part(BaseModel):
    asset_id: str
    part_model_id: str
    serial: str | None = None
    condition: PartCondition
    installed_in: str | None = None
    storage_location: StorageLocation | None = None

    @model_validator(mode="after")
    def check_single_location(self) -> Self:
        if self.installed_in and self.storage_location:
            raise ValueError(
                "A part cannot be installed in a device and in storage at the same time"
            )
        return self