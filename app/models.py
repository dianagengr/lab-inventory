from enum import StrEnum
from typing import Annotated, Literal, Self
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import (
    AwareDatetime,
    BaseModel,
    Field,
    IPvAnyInterface,
    IPvAnyNetwork,
    field_validator,
    model_validator,
)


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


class DeviceClass(StrEnum):
    RACK_SERVER = "rack_server"
    MINI_PC = "mini_pc"


class BaselineMode(StrEnum):
    MINIMUM = "minimum"
    EXACT = "exact"


class SiteType(StrEnum):
    LOCAL_LAB = "local_lab"
    LOCAL_COLO = "local_colo"
    REMOTE_COLO = "remote_colo"


class InfraType(StrEnum):
    SWITCH = "switch"
    PDU = "pdu"
    KVM = "kvm"


class RackItemType(StrEnum):
    SWITCH = "switch"
    PDU = "pdu"
    KVM = "kvm"
    PATCH_PANEL = "patch_panel"
    CABLE_MANAGER = "cable_manager"
    BLANKING_PANEL = "blanking_panel"
    SHELF = "shelf"


class MountType(StrEnum):
    RU = "ru"
    ZERO_U = "zero_u"


class PortMode(StrEnum):
    ACCESS = "access"
    TRUNK = "trunk"


class DiscoveryMethod(StrEnum):
    LLDP = "lldp"
    MAC_TABLE = "mac_table"
    MANUAL = "manual"


class EventSource(StrEnum):
    BMC_LOG = "bmc_log"
    OS_LOG = "os_log"
    SWITCH = "switch"
    PDU = "pdu"
    COLLECTOR = "collector"
    TOOL = "tool"


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class MetricName(StrEnum):
    POWER_WATTS = "power_watts"
    CPU_TEMP_C = "cpu_temp_c"
    INLET_TEMP_C = "inlet_temp_c"
    FAN_RPM = "fan_rpm"
    CPU_UTIL_PCT = "cpu_util_pct"


class BootStage(StrEnum):
    POWER = "power"
    OOB_MANAGEMENT = "oob_management"
    POST_BIOS = "post_bios"
    HARDWARE = "hardware"
    NETWORK = "network"
    PROVISIONING = "provisioning"
    OS = "os"


class CheckOutcome(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


class FindingCategory(StrEnum):
    FAILURE = "failure"
    RISK = "risk"
    TECH_DEBT = "tech_debt"
    INVENTORY = "inventory"


class ActionType(StrEnum):
    REPLACE_CABLE = "replace_cable"
    SEAT_OR_REPLACE_OPTIC = "seat_or_replace_optic"
    RUN_CABLE = "run_cable"
    SET_SWITCH_VLAN = "set_switch_vlan"
    SET_STABLE_IP = "set_stable_ip"
    UPDATE_FIRMWARE = "update_firmware"
    RESET_BMC = "reset_bmc"
    REPLACE_PART = "replace_part"
    INVESTIGATE = "investigate"


class RackLocation(BaseModel):
    kind: Literal["rack"] = "rack"
    site_id: str
    rack_id: str
    rack_unit: int = Field(ge=1, le=60)
    shelf_item_id: str | None = None


class StorageLocation(BaseModel):
    kind: Literal["storage"] = "storage"
    site_id: str
    room: str
    shelf: str
    bin: str | None = None


Location = Annotated[RackLocation | StorageLocation, Field(discriminator="kind")]

VlanId = Annotated[int, Field(ge=1, le=4094)]

OsiLayer = Literal[1, 2, 3, 4, 7]


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
    bios_version: str | None = None
    bmc_firmware: str | None = None
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


class BomLine(BaseModel):
    part_model_id: str
    quantity: int = Field(ge=1)


class Platform(BaseModel):
    platform_id: str
    make: str
    model: str
    device_class: DeviceClass
    height_u: int = Field(default=1, ge=1, le=10)
    has_bmc: bool
    bom: list[BomLine] = []

    @model_validator(mode="after")
    def check_unique_bom_lines(self) -> Self:
        part_ids = [line.part_model_id for line in self.bom]
        if len(part_ids) != len(set(part_ids)):
            raise ValueError(
                "Each part model should appear once in a BOM; use quantity instead"
            )
        return self


class Baseline(BaseModel):
    platform_id: str
    bios_version: str | None = None
    bmc_firmware: str | None = None
    mode: BaselineMode = BaselineMode.MINIMUM
    bios_settings: dict[str, str] = {}


class Site(BaseModel):
    site_id: str
    name: str
    site_type: SiteType
    region: str
    timezone: str
    purpose: str
    remote_hands_required: bool

    @field_validator("timezone")
    @classmethod
    def check_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError(f"Unknown time zone: {value}") from None
        return value


class Rack(BaseModel):
    rack_id: str
    site_id: str
    height_ru: int = Field(default=42, ge=1, le=60)
    power_capacity_watts: int | None = Field(default=None, ge=1)


class InfraDevice(BaseModel):
    infra_id: str
    infra_type: InfraType
    make: str
    model: str
    port_count: int = Field(ge=1)
    management_address: IpAssignment | None = None
    firmware: str | None = None


INFRA_ITEM_TYPES = {RackItemType.SWITCH, RackItemType.PDU, RackItemType.KVM}


class RackItem(BaseModel):
    item_id: str
    rack_id: str
    item_type: RackItemType
    mount: MountType = MountType.RU
    rack_unit: int | None = Field(default=None, ge=1, le=60)
    height_u: int = Field(default=1, ge=1, le=10)
    infra_id: str | None = None
    label: str | None = None

    @model_validator(mode="after")
    def check_mounting_and_reference(self) -> Self:
        if self.mount == MountType.ZERO_U and self.rack_unit is not None:
            raise ValueError(
                "Zero-U items mount on the side rails and have no rack unit"
            )
        if self.mount == MountType.RU and self.rack_unit is None:
            raise ValueError("RU-mounted items need a rack_unit")

        is_infra = self.item_type in INFRA_ITEM_TYPES
        if is_infra and self.infra_id is None:
            raise ValueError(f"{self.item_type} rack items must reference an infra_id")
        if not is_infra and self.infra_id is not None:
            raise ValueError(
                f"{self.item_type} items are passive and cannot reference an infra_id"
            )
        return self


class NetworkSegment(BaseModel):
    site_id: str
    role: InterfaceRole
    vlan_id: VlanId
    subnets: list[IPvAnyNetwork] = []
    name: str | None = None


class SwitchPort(BaseModel):
    switch_id: str
    port_name: str
    admin_up: bool = True
    link_up: bool
    speed_gbps: float | None = None
    module_present: bool | None = None
    mode: PortMode = PortMode.ACCESS
    access_vlan: VlanId | None = None
    allowed_vlans: list[VlanId] = []
    crc_errors: int = Field(default=0, ge=0)
    lldp_neighbor: str | None = None
    last_link_change: AwareDatetime | None = None

    @model_validator(mode="after")
    def check_vlan_config(self) -> Self:
        if self.mode == PortMode.ACCESS and self.allowed_vlans:
            raise ValueError(
                "Access ports carry one VLAN; use access_vlan, not allowed_vlans"
            )
        if self.mode == PortMode.TRUNK and self.access_vlan is not None:
            raise ValueError(
                "Trunk ports carry multiple VLANs; use allowed_vlans, not access_vlan"
            )
        return self


class Connection(BaseModel):
    device_asset_id: str
    interface_name: str
    switch_id: str
    port_name: str
    discovered_via: DiscoveryMethod
    last_seen: AwareDatetime


class Event(BaseModel):
    event_id: str
    subject_id: str
    timestamp: AwareDatetime
    source: EventSource
    severity: Severity
    message: str
    data: dict[str, str | int | float] = {}


class MetricSample(BaseModel):
    subject_id: str
    timestamp: AwareDatetime
    metric: MetricName
    sensor: str | None = None
    value: float


class RecommendedAction(BaseModel):
    action_type: ActionType
    needs_hands: bool
    description: str
    parameters: dict[str, str | int] = {}


class CheckResult(BaseModel):
    result_id: str
    subject_id: str
    check_name: str
    outcome: CheckOutcome
    category: FindingCategory | None = None
    stage: BootStage | None = None
    osi_layer: OsiLayer | None = None
    summary: str
    expected: str | None = None
    observed: str | None = None
    likely_cause: str | None = None
    recommended_action: RecommendedAction | None = None
    checked_at: AwareDatetime

    @model_validator(mode="after")
    def check_outcome_consistency(self) -> Self:
        failed = self.outcome == CheckOutcome.FAIL
        has_problem_details = (
            self.category or self.likely_cause or self.recommended_action
        )
        if not failed and has_problem_details:
            raise ValueError(
                "Only failed checks can carry a category, likely cause, or recommended action"
            )
        if failed and self.category is None:
            raise ValueError("Failed checks must have a category")
        return self
