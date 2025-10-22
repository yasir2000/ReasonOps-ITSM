"""
ITIL 4 Service Catalogue Management Practice Implementation

This module provides service catalogue/portfolio capabilities including:
- Service definition (business service, technical service, supporting service)
- Service offerings, plans, and pricing models
- Dependencies mapping to other services/CMDB CIs
- Customer-facing catalogue view with request templates
- Lifecycle management (pipeline, live, retired)
- SLA packages and support tiers
- Approval workflow stubs and policy checks
- Reporting and portfolio analytics
"""

import sys
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
from decimal import Decimal
from collections import defaultdict
import asyncio
import logging

# Add parent directory to path for local imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.service_value_system import Priority, Status, Impact, Urgency
except Exception:
    class Priority(Enum):
        LOW = "Low"; MEDIUM = "Medium"; HIGH = "High"; CRITICAL = "Critical"
    class Status(Enum):
        NEW = "New"; IN_PROGRESS = "In Progress"; PUBLISHED = "Published"; RETIRED = "Retired"
    class Impact(Enum):
        LOW = "Low"; MEDIUM = "Medium"; HIGH = "High"; CRITICAL = "Critical"
    class Urgency(Enum):
        LOW = "Low"; MEDIUM = "Medium"; HIGH = "High"; CRITICAL = "Critical"


class ServiceLifecycle(Enum):
    PIPELINE = "Pipeline"
    LIVE = "Live"
    RETIRED = "Retired"


class ServiceType(Enum):
    BUSINESS = "Business"
    TECHNICAL = "Technical"
    SUPPORTING = "Supporting"


class PricingModelType(Enum):
    FLAT = "Flat"
    TIERED = "Tiered"
    USAGE = "Usage Based"
    SUBSCRIPTION = "Subscription"


@dataclass
class PricingModel:
    type: PricingModelType = PricingModelType.SUBSCRIPTION
    currency: str = "USD"
    base_price: Decimal = Decimal("0.00")
    tiers: List[Tuple[int, Decimal]] = field(default_factory=list)  # (upto_units, price)
    unit: Optional[str] = None  # e.g., per user, per GB

    def estimate(self, quantity: int = 1) -> Decimal:
        if self.type == PricingModelType.FLAT:
            return self.base_price
        if self.type == PricingModelType.SUBSCRIPTION:
            return self.base_price * quantity
        if self.type == PricingModelType.USAGE and self.unit:
            return self.base_price * quantity
        if self.type == PricingModelType.TIERED and self.tiers:
            remaining = quantity
            total = Decimal("0.00")
            for upto, price in sorted(self.tiers, key=lambda x: x[0]):
                if remaining <= 0:
                    break
                take = min(remaining, upto)
                total += price * take
                remaining -= take
            if remaining > 0:
                total += self.base_price * remaining
            return total
        return self.base_price


@dataclass
class SLAPackage:
    name: str
    availability_target: float  # e.g., 99.9
    response_time_slo: str  # e.g., "4h" for P2
    support_hours: str  # e.g., "24x7" or "8x5"
    incident_prioritization: Dict[str, str] = field(default_factory=dict)


@dataclass
class ServiceOffering:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    pricing: PricingModel = field(default_factory=PricingModel)
    sla: SLAPackage = field(default_factory=lambda: SLAPackage("Standard", 99.9, "8h", "8x5"))
    request_template: Dict[str, Any] = field(default_factory=dict)
    eligibility_rules: List[str] = field(default_factory=list)


@dataclass
class ServiceDependency:
    to_service_id: str
    dependency_type: str = "Critical"  # Critical/Important/Optional


@dataclass
class Service:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    service_type: ServiceType = ServiceType.BUSINESS
    owner: str = "Service Owner"
    lifecycle: ServiceLifecycle = ServiceLifecycle.LIVE
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    offerings: List[ServiceOffering] = field(default_factory=list)
    dependencies: List[ServiceDependency] = field(default_factory=list)
    related_ci_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ApprovalPolicy:
    name: str
    conditions: List[str] = field(default_factory=list)
    approvers: List[str] = field(default_factory=list)
    auto_approve_under_amount: Optional[Decimal] = None

    def requires_approval(self, estimated_cost: Decimal) -> bool:
        if self.auto_approve_under_amount is not None and estimated_cost <= self.auto_approve_under_amount:
            return False
        return True


class ServiceCatalogueManager:
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.approval_policies: Dict[str, ApprovalPolicy] = {}
        self.logger = logging.getLogger(__name__)
        self._init_sample_catalogue()

    def _init_sample_catalogue(self):
        # Approval policies
        self.approval_policies["Standard"] = ApprovalPolicy(
            name="Standard", conditions=["Default policy"], approvers=["Service Owner"], auto_approve_under_amount=Decimal("500.00")
        )
        self.approval_policies["High Cost"] = ApprovalPolicy(
            name="High Cost", conditions=["> $500"], approvers=["Finance", "IT Director"], auto_approve_under_amount=None
        )

        # Services and offerings
        email = Service(
            name="Email Service",
            description="Managed corporate email with calendar and collaboration",
            service_type=ServiceType.BUSINESS,
            owner="Messaging Team",
            categories=["Collaboration", "Productivity"],
        )
        email.offerings = [
            ServiceOffering(
                name="Standard Mailbox",
                description="50GB mailbox, 8x5 support",
                pricing=PricingModel(PricingModelType.SUBSCRIPTION, "USD", Decimal("8.00"), unit="per user/month"),
                sla=SLAPackage("Standard", 99.9, "8h", "8x5"),
                request_template={"fields": ["userId", "department", "costCenter"], "auto_provision": True}
            ),
            ServiceOffering(
                name="Premium Mailbox",
                description="100GB mailbox, archiving, 24x7 support",
                pricing=PricingModel(PricingModelType.SUBSCRIPTION, "USD", Decimal("12.00"), unit="per user/month"),
                sla=SLAPackage("Premium", 99.95, "4h", "24x7"),
                request_template={"fields": ["userId", "managerApproval", "costCenter"], "auto_provision": False},
                eligibility_rules=["manager_approval_required"]
            )
        ]

        vm = Service(
            name="Virtual Machine Hosting",
            description="Provision and manage Windows/Linux VMs",
            service_type=ServiceType.TECHNICAL,
            owner="Cloud Platform Team",
            categories=["Compute", "IaaS"],
        )
        vm.offerings = [
            ServiceOffering(
                name="Small VM",
                description="2 vCPU, 8GB RAM",
                pricing=PricingModel(PricingModelType.USAGE, "USD", Decimal("0.12"), unit="per hour"),
                sla=SLAPackage("Standard", 99.9, "4h", "24x7"),
                request_template={"fields": ["os", "vCPU", "RAM", "network"], "defaults": {"vCPU": 2, "RAM": 8}}
            ),
            ServiceOffering(
                name="Large VM",
                description="8 vCPU, 32GB RAM",
                pricing=PricingModel(PricingModelType.USAGE, "USD", Decimal("0.50"), unit="per hour"),
                sla=SLAPackage("Premium", 99.95, "2h", "24x7"),
                request_template={"fields": ["os", "vCPU", "RAM", "network"], "defaults": {"vCPU": 8, "RAM": 32}}
            )
        ]
        vm.dependencies = [ServiceDependency(to_service_id=email.id, dependency_type="Important")]

        self.add_service(email)
        self.add_service(vm)

    def add_service(self, service: Service) -> str:
        self.services[service.id] = service
        return service.id

    def search_services(self, text: str = "", category: Optional[str] = None) -> List[Service]:
        results = []
        for s in self.services.values():
            if text and text.lower() not in (s.name + " " + s.description).lower():
                continue
            if category and category not in s.categories:
                continue
            results.append(s)
        return results

    def get_catalogue_view(self) -> List[Dict[str, Any]]:
        view = []
        for s in self.services.values():
            offerings = [
                {
                    "name": o.name,
                    "price": str(o.pricing.base_price),
                    "pricing_model": o.pricing.type.value,
                    "unit": o.pricing.unit,
                    "sla": {
                        "name": o.sla.name,
                        "availability": o.sla.availability_target,
                        "support": o.sla.support_hours
                    },
                }
                for o in s.offerings
            ]
            view.append({
                "service_id": s.id,
                "name": s.name,
                "type": s.service_type.value,
                "owner": s.owner,
                "categories": s.categories,
                "offerings": offerings
            })
        return view

    def estimate_request_cost(self, service_id: str, offering_name: str, quantity: int = 1) -> Optional[Decimal]:
        s = self.services.get(service_id)
        if not s:
            return None
        for o in s.offerings:
            if o.name == offering_name:
                return o.pricing.estimate(quantity)
        return None

    def check_approval_needed(self, estimated_cost: Decimal) -> Tuple[bool, List[str]]:
        policy = self.approval_policies.get("High Cost" if estimated_cost > Decimal("500.00") else "Standard")
        return policy.requires_approval(estimated_cost), policy.approvers

    def portfolio_analytics(self) -> Dict[str, Any]:
        by_type = defaultdict(int)
        by_category = defaultdict(int)
        offering_count = 0
        for s in self.services.values():
            by_type[s.service_type.value] += 1
            for c in s.categories:
                by_category[c] += 1
            offering_count += len(s.offerings)
        return {
            "total_services": len(self.services),
            "total_offerings": offering_count,
            "by_type": dict(by_type),
            "by_category": dict(by_category)
        }


async def main():
    print("🗂️ ITIL 4 Service Catalogue Management")
    print("=" * 50)
    scm = ServiceCatalogueManager()

    # Catalogue view
    print("\n📋 Catalogue (customer-facing):")
    view = scm.get_catalogue_view()
    print(f"Services: {len(view)}")
    for svc in view:
        print(f"  - {svc['name']} ({svc['type']}) | Offerings: {len(svc['offerings'])}")

    # Search demo
    print("\n🔎 Search for 'VM':")
    results = scm.search_services(text="VM")
    for r in results:
        print(f"  • {r.name} -> {', '.join(o.name for o in r.offerings)}")

    # Cost estimate + approval
    print("\n💵 Cost estimate & approval:")
    # pick the VM service
    vm_service = next((s for s in scm.services.values() if s.name.startswith("Virtual")), None)
    if vm_service:
        est = scm.estimate_request_cost(vm_service.id, "Large VM", quantity=100)  # 100 hours
        needs_approval, approvers = scm.check_approval_needed(est or Decimal("0"))
        print(f"Estimate for Large VM (100h): ${est}")
        print(f"Approval Needed: {'Yes' if needs_approval else 'No'} | Approvers: {', '.join(approvers)}")

    # Portfolio analytics
    print("\n📈 Portfolio Analytics:")
    analytics = scm.portfolio_analytics()
    print(f"Total Services: {analytics['total_services']}")
    print(f"Total Offerings: {analytics['total_offerings']}")
    print(f"By Type: {analytics['by_type']}")

    print("\n✅ Service Catalogue Demo Complete")


if __name__ == "__main__":
    asyncio.run(main())
