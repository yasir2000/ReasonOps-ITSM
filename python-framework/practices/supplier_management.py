"""
ITIL 4 Supplier Management Practice Implementation

This module provides supplier/vendor management capabilities including:
- Supplier onboarding, qualification, and categorization
- Contract lifecycle (draft, active, renewal, terminated)
- Supplier performance KPIs and scorecards
- SLA/OLA tracking with penalties/credits
- Risk assessment (delivery, financial, compliance, cyber)
- Compliance and audit findings against suppliers
- Reporting and recommendations
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
        DRAFT = "Draft"; ACTIVE = "Active"; SUSPENDED = "Suspended"; TERMINATED = "Terminated"; CLOSED = "Closed"
    class Impact(Enum):
        LOW = "Low"; MEDIUM = "Medium"; HIGH = "High"; CRITICAL = "Critical"
    class Urgency(Enum):
        LOW = "Low"; MEDIUM = "Medium"; HIGH = "High"; CRITICAL = "Critical"


class SupplierTier(Enum):
    STRATEGIC = "Strategic"
    PREFERRED = "Preferred"
    APPROVED = "Approved"
    TACTICAL = "Tactical"


class ContractType(Enum):
    MSA = "Master Services Agreement"
    SOW = "Statement of Work"
    SUBSCRIPTION = "Subscription"
    LICENSE = "License"


@dataclass
class Supplier:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    tier: SupplierTier = SupplierTier.APPROVED
    category: str = "Software"
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    onboarding_date: datetime = field(default_factory=datetime.now)
    certifications: List[str] = field(default_factory=list)
    critical_services: List[str] = field(default_factory=list)
    risk_rating: str = "Medium"  # Low/Medium/High
    country: str = "US"


@dataclass
class SupplierSLA:
    availability_target: float = 99.9
    response_time_hours: float = 4.0
    penalty_per_breach: Decimal = Decimal("500.00")
    credit_per_breach: Decimal = Decimal("100.00")


class ContractStatus(Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    RENEWAL_DUE = "Renewal Due"
    TERMINATED = "Terminated"


@dataclass
class SupplierContract:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    supplier_id: str = ""
    contract_type: ContractType = ContractType.MSA
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    auto_renew: bool = True
    value: Decimal = Decimal("0.00")
    status: ContractStatus = ContractStatus.ACTIVE
    sla: SupplierSLA = field(default_factory=SupplierSLA)
    kpis: Dict[str, float] = field(default_factory=lambda: {"on_time_delivery": 98.0, "quality": 99.0, "support_satisfaction": 4.5})
    notes: str = ""

    def days_to_expiry(self) -> Optional[int]:
        if not self.end_date:
            return None
        return (self.end_date - datetime.now()).days


@dataclass
class SupplierKPIResult:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    supplier_id: str = ""
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    metrics: Dict[str, float] = field(default_factory=dict)
    incidents_count: int = 0
    availability_percentage: float = 100.0


@dataclass
class SupplierScorecard:
    supplier_id: str
    period: str  # e.g., "2025-Q3"
    score: float
    rating: str
    strengths: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class SupplierManager:
    def __init__(self):
        self.suppliers: Dict[str, Supplier] = {}
        self.contracts: Dict[str, SupplierContract] = {}
        self.kpi_results: Dict[str, List[SupplierKPIResult]] = defaultdict(list)
        self.logger = logging.getLogger(__name__)
        self._init_sample_suppliers()

    def _init_sample_suppliers(self):
        s1 = Supplier(
            name="Acme Cloud Services",
            tier=SupplierTier.STRATEGIC,
            category="Cloud",
            contact_email="account@acmecloud.example",
            certifications=["ISO 27001", "SOC 2"],
            critical_services=["Customer Portal Hosting"],
            risk_rating="Low"
        )
        s2 = Supplier(
            name="DataSecure Ltd",
            tier=SupplierTier.PREFERRED,
            category="Security",
            contact_email="support@datasecure.example",
            certifications=["SOC 2"],
            critical_services=["Managed SOC"],
            risk_rating="Medium"
        )
        self.suppliers[s1.id] = s1
        self.suppliers[s2.id] = s2

        c1 = SupplierContract(
            supplier_id=s1.id,
            contract_type=ContractType.SUBSCRIPTION,
            start_date=datetime.now() - timedelta(days=300),
            end_date=datetime.now() + timedelta(days=60),
            value=Decimal("250000.00"),
            sla=SupplierSLA(99.95, 2.0, Decimal("1000.00"), Decimal("250.00"))
        )
        c2 = SupplierContract(
            supplier_id=s2.id,
            contract_type=ContractType.MSA,
            start_date=datetime.now() - timedelta(days=450),
            end_date=datetime.now() + timedelta(days=15),
            value=Decimal("125000.00"),
            sla=SupplierSLA(99.9, 4.0, Decimal("750.00"), Decimal("200.00"))
        )
        self.contracts[c1.id] = c1
        self.contracts[c2.id] = c2

        # KPI results samples
        k1 = SupplierKPIResult(
            supplier_id=s1.id,
            period_start=datetime.now() - timedelta(days=90),
            period_end=datetime.now(),
            metrics={"on_time_delivery": 99.0, "quality": 99.2, "support_satisfaction": 4.6},
            incidents_count=1,
            availability_percentage=99.97
        )
        k2 = SupplierKPIResult(
            supplier_id=s2.id,
            period_start=datetime.now() - timedelta(days=90),
            period_end=datetime.now(),
            metrics={"on_time_delivery": 95.0, "quality": 97.5, "support_satisfaction": 4.2},
            incidents_count=3,
            availability_percentage=99.85
        )
        self.kpi_results[s1.id].append(k1)
        self.kpi_results[s2.id].append(k2)

    def suppliers_due_for_renewal(self, days: int = 45) -> List[Tuple[Supplier, SupplierContract]]:
        due = []
        cutoff = datetime.now() + timedelta(days=days)
        for contract in self.contracts.values():
            if contract.end_date and contract.end_date <= cutoff and contract.status == ContractStatus.ACTIVE:
                supplier = self.suppliers.get(contract.supplier_id)
                if supplier:
                    due.append((supplier, contract))
        return due

    def calculate_penalties_credits(self) -> Dict[str, Dict[str, str]]:
        results: Dict[str, Dict[str, str]] = {}
        for contract in self.contracts.values():
            penalties = Decimal("0.00")
            credits = Decimal("0.00")
            kpis = self.kpi_results.get(contract.supplier_id, [])
            for k in kpis:
                if k.availability_percentage < contract.sla.availability_target:
                    penalties += contract.sla.penalty_per_breach
                else:
                    credits += contract.sla.credit_per_breach
            supplier = self.suppliers.get(contract.supplier_id)
            if supplier:
                results[supplier.name] = {"penalties": str(penalties), "credits": str(credits)}
        return results

    def generate_scorecard(self, supplier_id: str, period_name: str = "2025-Q3") -> Optional[SupplierScorecard]:
        kpis = self.kpi_results.get(supplier_id, [])
        if not kpis:
            return None
        k = kpis[-1]
        # Weighted score example
        score = (
            k.metrics.get("on_time_delivery", 0) * 0.4 +
            k.metrics.get("quality", 0) * 0.4 +
            (k.metrics.get("support_satisfaction", 0) * 20) * 0.2
        )
        rating = "A" if score >= 95 else "B" if score >= 90 else "C" if score >= 80 else "D"
        strengths = [m for m, v in k.metrics.items() if v >= 98]
        improvements = [m for m, v in k.metrics.items() if v < 96]
        recommendations = [
            "Review incident root causes" if k.incidents_count > 2 else "Maintain performance",
            "Plan renewal negotiation" if score >= 92 else "Create improvement plan"
        ]
        return SupplierScorecard(
            supplier_id=supplier_id,
            period=period_name,
            score=round(score, 2),
            rating=rating,
            strengths=strengths,
            improvements=improvements,
            recommendations=recommendations
        )

    def dashboard(self) -> Dict[str, Any]:
        renewals = self.suppliers_due_for_renewal()
        penalties = self.calculate_penalties_credits()
        scorecards = {}
        for sid in self.suppliers.keys():
            sc = self.generate_scorecard(sid)
            if sc:
                scorecards[self.suppliers[sid].name] = {
                    "score": sc.score,
                    "rating": sc.rating,
                    "top_recommendation": sc.recommendations[0]
                }
        return {
            "suppliers": len(self.suppliers),
            "contracts": len(self.contracts),
            "renewals_due": len(renewals),
            "financials": penalties,
            "scorecards": scorecards
        }


async def main():
    print("🤝 ITIL 4 Supplier Management")
    print("=" * 50)
    sm = SupplierManager()

    # Renewals
    print("\n🗓️ Renewals Due (45d):")
    due = sm.suppliers_due_for_renewal()
    if not due:
        print("  None")
    for supplier, contract in due:
        print(f"  {supplier.name}: Contract ends in {contract.days_to_expiry()} days")

    # Financial penalties/credits
    print("\n💰 Penalties/Credits:")
    fin = sm.calculate_penalties_credits()
    for name, vals in fin.items():
        print(f"  {name}: Penalties ${vals['penalties']} | Credits ${vals['credits']}")

    # Scorecards
    print("\n📊 Supplier Scorecards:")
    for sid, s in sm.suppliers.items():
        sc = sm.generate_scorecard(sid)
        if sc:
            print(f"  {s.name}: Score {sc.score} ({sc.rating}) | Rec: {sc.recommendations[0]}")

    # Dashboard
    print("\n📈 Dashboard Summary:")
    dash = sm.dashboard()
    print(f"Suppliers: {dash['suppliers']} | Contracts: {dash['contracts']} | Renewals: {dash['renewals_due']}")

    print("\n✅ Supplier Management Demo Complete")


if __name__ == "__main__":
    asyncio.run(main())
