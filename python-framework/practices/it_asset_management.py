"""
ITIL 4 IT Asset Management Practice Implementation

This module provides comprehensive IT asset management capabilities including:
- Asset lifecycle management from planning to disposal
- Financial tracking and cost management  
- Asset discovery and inventory management
- License management and compliance
- Asset relationships and dependencies
- Depreciation calculations and reporting
- Vendor and contract management
- Asset security and risk assessment
"""

import sys
import os
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import logging
import uuid
from decimal import Decimal
from collections import defaultdict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.service_value_system import Priority, Status, Impact, Urgency


class AssetType(Enum):
    """Types of IT assets"""
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    LICENSE = "License"
    INFRASTRUCTURE = "Infrastructure"
    NETWORK = "Network"
    SECURITY = "Security"
    MOBILE = "Mobile"
    CLOUD = "Cloud"
    VIRTUAL = "Virtual"
    DATA = "Data"
    DOCUMENTATION = "Documentation"
    SERVICE = "Service"


class AssetStatus(Enum):
    """Asset lifecycle status"""
    PLANNED = "Planned"
    ORDERED = "Ordered"
    RECEIVED = "Received"
    IN_STOCK = "In Stock"
    DEPLOYED = "Deployed"
    IN_USE = "In Use"
    IN_MAINTENANCE = "In Maintenance"
    RETIRED = "Retired"
    DISPOSED = "Disposed"
    LOST = "Lost"
    STOLEN = "Stolen"


class DepreciationMethod(Enum):
    """Asset depreciation methods"""
    STRAIGHT_LINE = "Straight Line"
    DECLINING_BALANCE = "Declining Balance"
    UNITS_OF_PRODUCTION = "Units of Production"
    SUM_OF_YEARS_DIGITS = "Sum of Years Digits"


class LicenseType(Enum):
    """Software license types"""
    PERPETUAL = "Perpetual"
    SUBSCRIPTION = "Subscription"
    VOLUME = "Volume"
    OEM = "OEM"
    TRIAL = "Trial"
    OPEN_SOURCE = "Open Source"
    FREEWARE = "Freeware"


class ContractType(Enum):
    """Contract types for assets"""
    PURCHASE = "Purchase"
    LEASE = "Lease"
    RENTAL = "Rental"
    MAINTENANCE = "Maintenance"
    SUPPORT = "Support"
    WARRANTY = "Warranty"


@dataclass
class FinancialDetails:
    """Financial information for an asset"""
    purchase_cost: Decimal = Decimal('0.00')
    current_value: Decimal = Decimal('0.00')
    depreciated_value: Decimal = Decimal('0.00')
    salvage_value: Decimal = Decimal('0.00')
    maintenance_cost_annual: Decimal = Decimal('0.00')
    depreciation_method: DepreciationMethod = DepreciationMethod.STRAIGHT_LINE
    useful_life_years: int = 5
    purchase_date: Optional[datetime] = None
    depreciation_start_date: Optional[datetime] = None
    currency: str = "USD"
    cost_center: Optional[str] = None
    budget_code: Optional[str] = None
    
    def calculate_depreciation(self, as_of_date: Optional[datetime] = None) -> Decimal:
        """Calculate current depreciation amount"""
        if not self.depreciation_start_date or not self.purchase_cost:
            return Decimal('0.00')
        
        calculation_date = as_of_date or datetime.now()
        
        if calculation_date < self.depreciation_start_date:
            return Decimal('0.00')
        
        # Calculate time elapsed
        time_elapsed = calculation_date - self.depreciation_start_date
        years_elapsed = Decimal(str(time_elapsed.days / 365.25))
        
        if self.depreciation_method == DepreciationMethod.STRAIGHT_LINE:
            if years_elapsed >= self.useful_life_years:
                return self.purchase_cost - self.salvage_value
            
            annual_depreciation = (self.purchase_cost - self.salvage_value) / self.useful_life_years
            return annual_depreciation * years_elapsed
        
        # Add other depreciation methods as needed
        return Decimal('0.00')
    
    def get_current_book_value(self, as_of_date: Optional[datetime] = None) -> Decimal:
        """Calculate current book value"""
        depreciation = self.calculate_depreciation(as_of_date)
        return max(self.purchase_cost - depreciation, self.salvage_value)


@dataclass
class LicenseDetails:
    """License-specific information"""
    license_key: Optional[str] = None
    license_type: LicenseType = LicenseType.PERPETUAL
    total_licenses: int = 1
    allocated_licenses: int = 0
    available_licenses: int = 1
    license_server: Optional[str] = None
    compliance_status: str = "Compliant"
    audit_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    auto_renewal: bool = False
    cost_per_license: Decimal = Decimal('0.00')
    
    def is_compliant(self) -> bool:
        """Check if license usage is compliant"""
        return self.allocated_licenses <= self.total_licenses
    
    def get_utilization_percentage(self) -> float:
        """Get license utilization percentage"""
        if self.total_licenses == 0:
            return 0.0
        return (self.allocated_licenses / self.total_licenses) * 100
    
    def days_to_expiry(self) -> Optional[int]:
        """Get days until license expiry"""
        if not self.expiry_date:
            return None
        return (self.expiry_date - datetime.now()).days


@dataclass
class MaintenanceContract:
    """Maintenance contract information"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    contract_number: str = ""
    vendor: str = ""
    contract_type: ContractType = ContractType.MAINTENANCE
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    cost: Decimal = Decimal('0.00')
    coverage_details: str = ""
    response_time_sla: str = ""
    contact_info: Dict[str, str] = field(default_factory=dict)
    auto_renewal: bool = False
    notification_days: int = 30  # Days before expiry to notify
    
    def is_active(self) -> bool:
        """Check if contract is currently active"""
        now = datetime.now()
        return (self.start_date is None or self.start_date <= now) and \
               (self.end_date is None or self.end_date >= now)
    
    def days_to_expiry(self) -> Optional[int]:
        """Get days until contract expiry"""
        if not self.end_date:
            return None
        return (self.end_date - datetime.now()).days


@dataclass
class ITAsset:
    """Comprehensive IT Asset representation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    asset_tag: Optional[str] = None
    serial_number: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    
    # Classification
    asset_type: AssetType = AssetType.HARDWARE
    category: str = ""
    subcategory: str = ""
    
    # Status and lifecycle
    status: AssetStatus = AssetStatus.PLANNED
    location: Optional[str] = None
    owner: Optional[str] = None
    custodian: Optional[str] = None
    user: Optional[str] = None
    
    # Dates
    created_date: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    install_date: Optional[datetime] = None
    last_audit_date: Optional[datetime] = None
    next_audit_date: Optional[datetime] = None
    
    # Financial information
    financial: FinancialDetails = field(default_factory=FinancialDetails)
    
    # License information (for software assets)
    license: Optional[LicenseDetails] = None
    
    # Technical specifications
    specifications: Dict[str, Any] = field(default_factory=dict)
    
    # Relationships
    parent_asset_id: Optional[str] = None
    child_asset_ids: List[str] = field(default_factory=list)
    related_ci_id: Optional[str] = None  # Link to CMDB CI
    
    # Contracts and warranties
    maintenance_contracts: List[MaintenanceContract] = field(default_factory=list)
    warranty_expiry: Optional[datetime] = None
    
    # Security and compliance
    security_classification: str = "Public"
    compliance_requirements: List[str] = field(default_factory=list)
    vulnerability_scan_date: Optional[datetime] = None
    
    # Custom attributes
    custom_attributes: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    
    def add_maintenance_contract(self, contract: MaintenanceContract):
        """Add a maintenance contract"""
        self.maintenance_contracts.append(contract)
        self.last_modified = datetime.now()
    
    def get_active_contracts(self) -> List[MaintenanceContract]:
        """Get all active maintenance contracts"""
        return [contract for contract in self.maintenance_contracts if contract.is_active()]
    
    def get_total_cost_of_ownership(self, years: int = 5) -> Decimal:
        """Calculate total cost of ownership"""
        tco = self.financial.purchase_cost
        
        # Add annual maintenance costs
        tco += self.financial.maintenance_cost_annual * years
        
        # Add contract costs
        for contract in self.maintenance_contracts:
            if contract.is_active():
                tco += contract.cost
        
        return tco
    
    def is_due_for_audit(self) -> bool:
        """Check if asset is due for audit"""
        if not self.next_audit_date:
            return True
        return datetime.now() >= self.next_audit_date
    
    def update_status(self, new_status: AssetStatus, reason: str = ""):
        """Update asset status with tracking"""
        old_status = self.status
        self.status = new_status
        self.last_modified = datetime.now()
        
        # Add to custom attributes for audit trail
        if "status_history" not in self.custom_attributes:
            self.custom_attributes["status_history"] = []
        
        self.custom_attributes["status_history"].append({
            "timestamp": datetime.now().isoformat(),
            "from_status": old_status.value,
            "to_status": new_status.value,
            "reason": reason
        })


class AssetDiscoveryEngine:
    """Asset discovery and inventory management"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.discovery_rules: List[Dict[str, Any]] = []
    
    def add_discovery_rule(self, rule: Dict[str, Any]):
        """Add an asset discovery rule"""
        self.discovery_rules.append(rule)
    
    async def discover_assets(self, discovery_method: str = "network_scan") -> List[Dict[str, Any]]:
        """Discover assets using specified method"""
        
        # Mock discovery results for demonstration
        discovered_assets = []
        
        if discovery_method == "network_scan":
            discovered_assets = [
                {
                    "name": "Discovered Server 01",
                    "ip_address": "10.1.1.50",
                    "mac_address": "00:11:22:33:44:55",
                    "os": "Windows Server 2019",
                    "asset_type": "Hardware",
                    "category": "Server",
                    "discovery_method": "Network Scan",
                    "confidence": 95
                },
                {
                    "name": "Discovered Workstation 05",
                    "ip_address": "10.1.2.15",
                    "mac_address": "AA:BB:CC:DD:EE:FF",
                    "os": "Windows 10",
                    "asset_type": "Hardware",
                    "category": "Workstation",
                    "discovery_method": "Network Scan",
                    "confidence": 90
                }
            ]
        
        elif discovery_method == "software_inventory":
            discovered_assets = [
                {
                    "name": "Microsoft Office 365",
                    "version": "2021",
                    "vendor": "Microsoft",
                    "asset_type": "Software",
                    "category": "Productivity Suite",
                    "installed_on": ["WS001", "WS002", "WS003"],
                    "license_required": True,
                    "discovery_method": "Software Inventory",
                    "confidence": 100
                }
            ]
        
        self.logger.info(f"Discovered {len(discovered_assets)} assets using {discovery_method}")
        return discovered_assets
    
    def match_discovered_asset(self, discovered_asset: Dict[str, Any], 
                              existing_assets: List[ITAsset]) -> Optional[ITAsset]:
        """Match discovered asset with existing asset"""
        
        # Simple matching logic - can be enhanced
        for asset in existing_assets:
            # Match by MAC address if available
            if (discovered_asset.get("mac_address") and 
                asset.specifications.get("mac_address") == discovered_asset["mac_address"]):
                return asset
            
            # Match by IP address
            if (discovered_asset.get("ip_address") and 
                asset.specifications.get("ip_address") == discovered_asset["ip_address"]):
                return asset
            
            # Match by name similarity
            if discovered_asset.get("name") and asset.name:
                if discovered_asset["name"].lower() in asset.name.lower():
                    return asset
        
        return None


class AssetManager:
    """Main IT Asset Management system"""
    
    def __init__(self):
        self.assets: Dict[str, ITAsset] = {}
        self.discovery_engine = AssetDiscoveryEngine()
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.stats = {
            "total_assets": 0,
            "assets_by_type": defaultdict(int),
            "assets_by_status": defaultdict(int),
            "total_value": Decimal('0.00'),
            "assets_due_for_audit": 0,
            "expiring_contracts": 0,
            "license_compliance_issues": 0
        }
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample asset data"""
        
        # Sample hardware assets
        server_asset = ITAsset(
            name="Production Web Server 01",
            description="Primary web server for customer portal",
            asset_tag="SRV-001",
            serial_number="SN123456789",
            model="PowerEdge R740",
            manufacturer="Dell",
            asset_type=AssetType.HARDWARE,
            category="Server",
            subcategory="Rack Server",
            status=AssetStatus.IN_USE,
            location="Data Center 1",
            owner="IT Operations",
            custodian="System Administrator"
        )
        
        # Set financial details
        server_asset.financial = FinancialDetails(
            purchase_cost=Decimal('15000.00'),
            current_value=Decimal('12000.00'),
            salvage_value=Decimal('1000.00'),
            maintenance_cost_annual=Decimal('2000.00'),
            useful_life_years=5,
            purchase_date=datetime.now() - timedelta(days=365),
            depreciation_start_date=datetime.now() - timedelta(days=365),
            cost_center="IT-OPS-001"
        )
        
        # Add specifications
        server_asset.specifications = {
            "cpu": "Intel Xeon Silver 4214",
            "cores": 12,
            "memory_gb": 64,
            "storage_gb": 2000,
            "network_ports": 4,
            "power_supply": "Dual 750W",
            "rack_units": 2
        }
        
        # Add maintenance contract
        maintenance_contract = MaintenanceContract(
            contract_number="MAINT-001",
            vendor="Dell Support",
            contract_type=ContractType.MAINTENANCE,
            start_date=datetime.now() - timedelta(days=300),
            end_date=datetime.now() + timedelta(days=65),
            cost=Decimal('2500.00'),
            coverage_details="24x7 hardware support with 4-hour response",
            response_time_sla="4 hours"
        )
        
        server_asset.add_maintenance_contract(maintenance_contract)
        
        # Sample software asset
        office_asset = ITAsset(
            name="Microsoft Office 365 E3",
            description="Productivity suite for all employees",
            asset_type=AssetType.SOFTWARE,
            category="Productivity Suite",
            status=AssetStatus.IN_USE,
            owner="IT Operations"
        )
        
        # Set license details
        office_asset.license = LicenseDetails(
            license_type=LicenseType.SUBSCRIPTION,
            total_licenses=100,
            allocated_licenses=85,
            available_licenses=15,
            cost_per_license=Decimal('22.00'),
            expiry_date=datetime.now() + timedelta(days=180),
            auto_renewal=True
        )
        
        office_asset.financial = FinancialDetails(
            purchase_cost=Decimal('2200.00'),  # Monthly cost * 12
            maintenance_cost_annual=Decimal('26400.00'),  # 100 licenses * $22 * 12
            cost_center="IT-SOFTWARE-001"
        )
        
        # Sample network asset
        switch_asset = ITAsset(
            name="Core Network Switch 01",
            description="48-port Gigabit switch for main network",
            asset_tag="NET-001",
            serial_number="SN987654321",
            model="Catalyst 2960-X",
            manufacturer="Cisco",
            asset_type=AssetType.NETWORK,
            category="Switch",
            status=AssetStatus.IN_USE,
            location="Network Closet A",
            owner="Network Team"
        )
        
        switch_asset.financial = FinancialDetails(
            purchase_cost=Decimal('3500.00'),
            salvage_value=Decimal('200.00'),
            useful_life_years=7,
            purchase_date=datetime.now() - timedelta(days=730),
            depreciation_start_date=datetime.now() - timedelta(days=730)
        )
        
        switch_asset.specifications = {
            "ports": 48,
            "port_type": "Gigabit Ethernet",
            "uplink_ports": 4,
            "poe_support": True,
            "management": "Web, CLI, SNMP"
        }
        
        # Add assets to system
        self.add_asset(server_asset)
        self.add_asset(office_asset)
        self.add_asset(switch_asset)
    
    def add_asset(self, asset: ITAsset) -> str:
        """Add an asset to the system"""
        
        self.assets[asset.id] = asset
        self._update_statistics()
        
        self.logger.info(f"Added asset {asset.id}: {asset.name}")
        return asset.id
    
    def get_asset(self, asset_id: str) -> Optional[ITAsset]:
        """Get an asset by ID"""
        return self.assets.get(asset_id)
    
    def update_asset(self, asset_id: str, updates: Dict[str, Any]) -> bool:
        """Update an asset"""
        
        asset = self.assets.get(asset_id)
        if not asset:
            return False
        
        # Update basic fields
        for key, value in updates.items():
            if hasattr(asset, key) and key not in ['id', 'created_date']:
                setattr(asset, key, value)
        
        asset.last_modified = datetime.now()
        self._update_statistics()
        
        self.logger.info(f"Updated asset {asset_id}")
        return True
    
    def search_assets(self, criteria: Dict[str, Any]) -> List[ITAsset]:
        """Search for assets based on criteria"""
        
        results = []
        
        for asset in self.assets.values():
            match = True
            
            # Check basic criteria
            for key, value in criteria.items():
                if key == "asset_type" and asset.asset_type.value != value:
                    match = False
                    break
                elif key == "status" and asset.status.value != value:
                    match = False
                    break
                elif key == "category" and asset.category != value:
                    match = False
                    break
                elif key == "owner" and asset.owner != value:
                    match = False
                    break
                elif key == "location" and asset.location != value:
                    match = False
                    break
                elif key == "manufacturer" and asset.manufacturer != value:
                    match = False
                    break
                elif key == "name" and value.lower() not in (asset.name or "").lower():
                    match = False
                    break
            
            if match:
                results.append(asset)
        
        return results
    
    def get_assets_due_for_audit(self) -> List[ITAsset]:
        """Get assets that are due for audit"""
        return [asset for asset in self.assets.values() if asset.is_due_for_audit()]
    
    def get_expiring_contracts(self, days_ahead: int = 30) -> List[Tuple[ITAsset, MaintenanceContract]]:
        """Get assets with expiring maintenance contracts"""
        
        expiring = []
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        
        for asset in self.assets.values():
            for contract in asset.maintenance_contracts:
                if (contract.end_date and 
                    contract.end_date <= cutoff_date and 
                    contract.is_active()):
                    expiring.append((asset, contract))
        
        return expiring
    
    def get_license_compliance_report(self) -> Dict[str, Any]:
        """Generate license compliance report"""
        
        report = {
            "total_software_assets": 0,
            "compliant_assets": 0,
            "non_compliant_assets": 0,
            "over_allocated": [],
            "expiring_soon": [],
            "utilization_summary": []
        }
        
        for asset in self.assets.values():
            if asset.asset_type == AssetType.SOFTWARE and asset.license:
                report["total_software_assets"] += 1
                
                if asset.license.is_compliant():
                    report["compliant_assets"] += 1
                else:
                    report["non_compliant_assets"] += 1
                    report["over_allocated"].append({
                        "asset_id": asset.id,
                        "asset_name": asset.name,
                        "total_licenses": asset.license.total_licenses,
                        "allocated_licenses": asset.license.allocated_licenses,
                        "over_allocation": asset.license.allocated_licenses - asset.license.total_licenses
                    })
                
                # Check for expiring licenses
                days_to_expiry = asset.license.days_to_expiry()
                if days_to_expiry is not None and days_to_expiry <= 30:
                    report["expiring_soon"].append({
                        "asset_id": asset.id,
                        "asset_name": asset.name,
                        "expiry_date": asset.license.expiry_date.isoformat() if asset.license.expiry_date else None,
                        "days_to_expiry": days_to_expiry
                    })
                
                # Utilization summary
                report["utilization_summary"].append({
                    "asset_id": asset.id,
                    "asset_name": asset.name,
                    "utilization_percentage": asset.license.get_utilization_percentage(),
                    "total_licenses": asset.license.total_licenses,
                    "allocated_licenses": asset.license.allocated_licenses
                })
        
        return report
    
    def calculate_portfolio_value(self, as_of_date: Optional[datetime] = None) -> Dict[str, Decimal]:
        """Calculate total portfolio value"""
        
        calculation_date = as_of_date or datetime.now()
        
        portfolio_value = {
            "total_purchase_cost": Decimal('0.00'),
            "total_current_book_value": Decimal('0.00'),
            "total_depreciation": Decimal('0.00'),
            "by_asset_type": defaultdict(lambda: Decimal('0.00')),
            "by_status": defaultdict(lambda: Decimal('0.00'))
        }
        
        for asset in self.assets.values():
            purchase_cost = asset.financial.purchase_cost
            book_value = asset.financial.get_current_book_value(calculation_date)
            depreciation = asset.financial.calculate_depreciation(calculation_date)
            
            portfolio_value["total_purchase_cost"] += purchase_cost
            portfolio_value["total_current_book_value"] += book_value
            portfolio_value["total_depreciation"] += depreciation
            
            portfolio_value["by_asset_type"][asset.asset_type.value] += book_value
            portfolio_value["by_status"][asset.status.value] += book_value
        
        return portfolio_value
    
    def generate_asset_report(self, report_type: str = "summary") -> Dict[str, Any]:
        """Generate comprehensive asset report"""
        
        if report_type == "summary":
            return self._generate_summary_report()
        elif report_type == "financial":
            return self._generate_financial_report()
        elif report_type == "compliance":
            return self._generate_compliance_report()
        else:
            return {"error": "Unknown report type"}
    
    def _generate_summary_report(self) -> Dict[str, Any]:
        """Generate summary asset report"""
        
        return {
            "report_type": "Asset Summary",
            "generated_date": datetime.now().isoformat(),
            "statistics": self.get_statistics(),
            "asset_distribution": {
                "by_type": dict(self.stats["assets_by_type"]),
                "by_status": dict(self.stats["assets_by_status"])
            },
            "top_assets_by_value": self._get_top_assets_by_value(10),
            "upcoming_actions": {
                "assets_due_for_audit": len(self.get_assets_due_for_audit()),
                "expiring_contracts": len(self.get_expiring_contracts()),
                "expiring_licenses": len([
                    asset for asset in self.assets.values()
                    if (asset.license and asset.license.days_to_expiry() is not None and 
                        asset.license.days_to_expiry() <= 30)
                ])
            }
        }
    
    def _generate_financial_report(self) -> Dict[str, Any]:
        """Generate financial asset report"""
        
        portfolio_value = self.calculate_portfolio_value()
        
        return {
            "report_type": "Financial Asset Report",
            "generated_date": datetime.now().isoformat(),
            "portfolio_value": {
                "total_purchase_cost": str(portfolio_value["total_purchase_cost"]),
                "total_current_book_value": str(portfolio_value["total_current_book_value"]),
                "total_depreciation": str(portfolio_value["total_depreciation"]),
                "depreciation_percentage": float(
                    (portfolio_value["total_depreciation"] / 
                     max(portfolio_value["total_purchase_cost"], Decimal('0.01'))) * 100
                )
            },
            "value_by_type": {
                asset_type: str(value) 
                for asset_type, value in portfolio_value["by_asset_type"].items()
            },
            "annual_maintenance_costs": self._calculate_annual_maintenance_costs(),
            "tco_analysis": self._calculate_tco_analysis()
        }
    
    def _generate_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance asset report"""
        
        license_report = self.get_license_compliance_report()
        
        return {
            "report_type": "Asset Compliance Report",
            "generated_date": datetime.now().isoformat(),
            "license_compliance": license_report,
            "audit_status": {
                "total_assets": len(self.assets),
                "assets_due_for_audit": len(self.get_assets_due_for_audit()),
                "last_audit_completion": self._get_last_audit_completion_rate()
            },
            "contract_status": {
                "total_contracts": self._get_total_contracts(),
                "expiring_contracts": len(self.get_expiring_contracts()),
                "expired_contracts": len(self.get_expiring_contracts(-365))  # Already expired
            }
        }
    
    def _get_top_assets_by_value(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top assets by current book value"""
        
        asset_values = []
        for asset in self.assets.values():
            book_value = asset.financial.get_current_book_value()
            asset_values.append({
                "asset_id": asset.id,
                "asset_name": asset.name,
                "asset_type": asset.asset_type.value,
                "current_book_value": str(book_value),
                "purchase_cost": str(asset.financial.purchase_cost)
            })
        
        # Sort by current book value
        asset_values.sort(key=lambda x: Decimal(x["current_book_value"]), reverse=True)
        return asset_values[:limit]
    
    def _calculate_annual_maintenance_costs(self) -> Decimal:
        """Calculate total annual maintenance costs"""
        
        total_cost = Decimal('0.00')
        
        for asset in self.assets.values():
            total_cost += asset.financial.maintenance_cost_annual
            
            for contract in asset.get_active_contracts():
                if contract.contract_type == ContractType.MAINTENANCE:
                    total_cost += contract.cost
        
        return total_cost
    
    def _calculate_tco_analysis(self) -> Dict[str, Any]:
        """Calculate Total Cost of Ownership analysis"""
        
        tco_by_type = defaultdict(lambda: Decimal('0.00'))
        
        for asset in self.assets.values():
            tco = asset.get_total_cost_of_ownership()
            tco_by_type[asset.asset_type.value] += tco
        
        return {
            "by_asset_type": {asset_type: str(tco) for asset_type, tco in tco_by_type.items()},
            "total_tco": str(sum(tco_by_type.values()))
        }
    
    def _get_last_audit_completion_rate(self) -> float:
        """Get audit completion rate"""
        
        audited_assets = len([
            asset for asset in self.assets.values() 
            if asset.last_audit_date and 
            asset.last_audit_date >= datetime.now() - timedelta(days=365)
        ])
        
        return (audited_assets / max(len(self.assets), 1)) * 100
    
    def _get_total_contracts(self) -> int:
        """Get total number of contracts"""
        
        total = 0
        for asset in self.assets.values():
            total += len(asset.maintenance_contracts)
        return total
    
    def _update_statistics(self):
        """Update system statistics"""
        
        self.stats = {
            "total_assets": len(self.assets),
            "assets_by_type": defaultdict(int),
            "assets_by_status": defaultdict(int),
            "total_value": Decimal('0.00'),
            "assets_due_for_audit": 0,
            "expiring_contracts": 0,
            "license_compliance_issues": 0
        }
        
        for asset in self.assets.values():
            self.stats["assets_by_type"][asset.asset_type.value] += 1
            self.stats["assets_by_status"][asset.status.value] += 1
            self.stats["total_value"] += asset.financial.get_current_book_value()
            
            if asset.is_due_for_audit():
                self.stats["assets_due_for_audit"] += 1
            
            if asset.license and not asset.license.is_compliant():
                self.stats["license_compliance_issues"] += 1
        
        self.stats["expiring_contracts"] = len(self.get_expiring_contracts())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current asset management statistics"""
        return {
            **self.stats,
            "total_value": str(self.stats["total_value"])
        }
    
    async def run_asset_discovery(self, discovery_method: str = "network_scan") -> Dict[str, Any]:
        """Run asset discovery and return results"""
        
        discovered_assets = await self.discovery_engine.discover_assets(discovery_method)
        
        discovery_results = {
            "discovery_method": discovery_method,
            "discovery_date": datetime.now().isoformat(),
            "total_discovered": len(discovered_assets),
            "new_assets": [],
            "matched_assets": [],
            "unmatched_assets": []
        }
        
        existing_assets = list(self.assets.values())
        
        for discovered in discovered_assets:
            matched_asset = self.discovery_engine.match_discovered_asset(discovered, existing_assets)
            
            if matched_asset:
                discovery_results["matched_assets"].append({
                    "discovered": discovered,
                    "matched_asset_id": matched_asset.id,
                    "matched_asset_name": matched_asset.name
                })
            else:
                discovery_results["new_assets"].append(discovered)
                discovery_results["unmatched_assets"].append(discovered)
        
        return discovery_results


async def main():
    """Main function to demonstrate IT asset management"""
    print("💰 ITIL 4 IT Asset Management")
    print("=" * 50)
    
    # Initialize asset manager
    asset_manager = AssetManager()
    
    print("✅ Asset Manager initialized with sample data")
    
    # Display statistics
    stats = asset_manager.get_statistics()
    print(f"\n📊 Asset Management Statistics:")
    print(f"Total Assets: {stats['total_assets']}")
    print(f"Total Value: ${stats['total_value']}")
    print(f"Assets Due for Audit: {stats['assets_due_for_audit']}")
    print(f"Expiring Contracts: {stats['expiring_contracts']}")
    print(f"License Compliance Issues: {stats['license_compliance_issues']}")
    
    print(f"\nAssets by Type:")
    for asset_type, count in stats['assets_by_type'].items():
        print(f"  {asset_type}: {count}")
    
    print(f"\nAssets by Status:")
    for status, count in stats['assets_by_status'].items():
        print(f"  {status}: {count}")
    
    # Show sample assets
    print(f"\n📋 Sample Assets:")
    for asset in list(asset_manager.assets.values())[:3]:
        print(f"  {asset.name}:")
        print(f"    Type: {asset.asset_type.value}")
        print(f"    Status: {asset.status.value}")
        print(f"    Current Value: ${asset.financial.get_current_book_value()}")
        if asset.license:
            print(f"    License Utilization: {asset.license.get_utilization_percentage():.1f}%")
    
    # Financial reporting
    print(f"\n💰 Financial Analysis:")
    financial_report = asset_manager.generate_asset_report("financial")
    portfolio = financial_report["portfolio_value"]
    
    print(f"Total Purchase Cost: ${portfolio['total_purchase_cost']}")
    print(f"Current Book Value: ${portfolio['total_current_book_value']}")
    print(f"Total Depreciation: ${portfolio['total_depreciation']}")
    print(f"Depreciation Rate: {portfolio['depreciation_percentage']:.1f}%")
    
    print(f"\nValue by Asset Type:")
    for asset_type, value in financial_report["value_by_type"].items():
        print(f"  {asset_type}: ${value}")
    
    # License compliance
    print(f"\n🔒 License Compliance Report:")
    license_report = asset_manager.get_license_compliance_report()
    
    print(f"Total Software Assets: {license_report['total_software_assets']}")
    print(f"Compliant Assets: {license_report['compliant_assets']}")
    print(f"Non-Compliant Assets: {license_report['non_compliant_assets']}")
    
    if license_report["over_allocated"]:
        print(f"\nOver-Allocated Licenses:")
        for over_alloc in license_report["over_allocated"]:
            print(f"  {over_alloc['asset_name']}: {over_alloc['over_allocation']} over limit")
    
    if license_report["expiring_soon"]:
        print(f"\nExpiring Licenses:")
        for expiring in license_report["expiring_soon"]:
            print(f"  {expiring['asset_name']}: {expiring['days_to_expiry']} days")
    
    # Contract management
    print(f"\n📄 Contract Management:")
    expiring_contracts = asset_manager.get_expiring_contracts()
    
    if expiring_contracts:
        print(f"Expiring Contracts ({len(expiring_contracts)}):")
        for asset, contract in expiring_contracts:
            days_to_expiry = contract.days_to_expiry()
            print(f"  {asset.name}: {contract.contract_number} expires in {days_to_expiry} days")
    else:
        print("No contracts expiring in the next 30 days")
    
    # Asset discovery demo
    print(f"\n🔍 Asset Discovery Demo:")
    
    discovery_results = await asset_manager.run_asset_discovery("network_scan")
    print(f"Discovery Method: {discovery_results['discovery_method']}")
    print(f"Total Discovered: {discovery_results['total_discovered']}")
    print(f"New Assets: {len(discovery_results['new_assets'])}")
    print(f"Matched Assets: {len(discovery_results['matched_assets'])}")
    
    if discovery_results["new_assets"]:
        print(f"\nNew Assets Found:")
        for new_asset in discovery_results["new_assets"]:
            print(f"  {new_asset['name']} ({new_asset['category']})")
    
    # Audit management
    print(f"\n📝 Audit Management:")
    
    assets_due = asset_manager.get_assets_due_for_audit()
    print(f"Assets Due for Audit: {len(assets_due)}")
    
    for asset in assets_due[:3]:  # Show first 3
        print(f"  {asset.name} - Last audit: {asset.last_audit_date or 'Never'}")
    
    # Search functionality
    print(f"\n🔍 Asset Search Demo:")
    
    # Search for hardware assets
    hardware_assets = asset_manager.search_assets({"asset_type": "Hardware"})
    print(f"Hardware Assets: {len(hardware_assets)}")
    
    # Search for assets in production
    production_assets = asset_manager.search_assets({"status": "In Use"})
    print(f"In Use Assets: {len(production_assets)}")
    
    # Search by manufacturer
    dell_assets = asset_manager.search_assets({"manufacturer": "Dell"})
    print(f"Dell Assets: {len(dell_assets)}")
    
    # Top assets by value
    print(f"\n💎 Top Assets by Value:")
    summary_report = asset_manager.generate_asset_report("summary")
    
    for i, asset_info in enumerate(summary_report["top_assets_by_value"][:5], 1):
        print(f"  {i}. {asset_info['asset_name']}: ${asset_info['current_book_value']}")
    
    print(f"\n🎉 IT Asset Management Demo Complete!")
    print("Key Features Demonstrated:")
    print("✅ Complete asset lifecycle management")
    print("✅ Financial tracking and depreciation")
    print("✅ License management and compliance")
    print("✅ Contract and warranty tracking")
    print("✅ Asset discovery and inventory")
    print("✅ Comprehensive reporting and analytics")
    print("✅ Audit management and compliance")


if __name__ == "__main__":
    asyncio.run(main())