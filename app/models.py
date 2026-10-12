from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, IPvAnyInterface, field_validator, model_validator


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
    SLAAC_EUI64 = "slaac_eui64"
    SLAAC_PRIVACY = "slaac_privacy"


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


class InterfaceRole(StrEnum):
    BMC = "bmc"
    OS = "os"


class ManagementPathType(StrEnum):
    BMC_REDFISH = "bmc_redfish"
    BMC_IPMI = "bmc_ipmi"
    KVM = "kvm"
    PDU_OUTLET = "pdu_outlet"
    IN_BAND_SSH = "in_band_ssh"


class ProvisioningType(StrEnum):
    MANAGED = "managed"
    LOCAL = "local"


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


class IpAssignment(BaseModel):
    address: IPvAnyInterface
    mode: IpMode

    @model_validator(mode="after")
    def check_mode_matches_family(self) -> Self:
        is_slaac = self.mode in (IpMode.SLAAC_EUI64, IpMode.SLAAC_PRIVACY)
        if is_slaac and self.address.version != 6:
            raise ValueError("SLAAC modes apply only to IPv6 addresses")
        return self


class Interface(BaseModel):
    name: str
    role: InterfaceRole
    mac: str
    speed_gbps: float | None = None
    addresses: list[IpAssignment] = []
    ip_policy: IpPolicy = IpPolicy.STABLE_REQUIRED
    vlan: int | None = Field(default=None, ge=1, le=4094)

    @field_validator("mac", mode="before")
    @classmethod
    def normalize_mac(cls, value: str) -> str:
        digits = value.lower().replace(":", "").replace("-", "").replace(".", "")
        if len(digits) != 12 or any(c not in "0123456789abcdef" for c in digits):
            raise ValueError(f"Invalid MAC address: {value}")
        return ":".join(digits[i : i + 2] for i in range(0, 12, 2))


class ManagementPath(BaseModel):
    path_type: ManagementPathType
    target: str
    port: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def check_port_required(self) -> Self:
        needs_port = self.path_type in (
            ManagementPathType.KVM,
            ManagementPathType.PDU_OUTLET,
        )
        if needs_port and self.port is None:
            raise ValueError(f"{self.path_type} paths require a port number")
        return self


INTERFACE_PATH_TYPES = {
    ManagementPathType.BMC_REDFISH,
    ManagementPathType.BMC_IPMI,
    ManagementPathType.IN_BAND_SSH,
}


class Device(BaseModel):
    asset_id: str
    hostname: str | None = None
    serial: str | None = None
    platform_id: str
    location: Location | None = None
    status: DeviceStatus
    condition: DeviceCondition | None = None
    provisioning: ProvisioningType
    assigned_to: str | None = None
    interfaces: list[Interface] = []
    management_paths: list[ManagementPath] = []

    @model_validator(mode="after")
    def check_interfaces_and_paths(self) -> Self:
        names = [interface.name for interface in self.interfaces]
        if len(names) != len(set(names)):
            raise ValueError("Interface names must be unique within a device")

        macs = [interface.mac for interface in self.interfaces]
        if len(macs) != len(set(macs)):
            raise ValueError("MAC addresses must be unique within a device")

        for path in self.management_paths:
            if path.path_type in INTERFACE_PATH_TYPES and path.target not in names:
                raise ValueError(
                    f"{path.path_type} path targets interface '{path.target}', "
                    f"which does not exist on this device"
                )
        return self
