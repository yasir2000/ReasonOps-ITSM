"""
ITIL 4 Financial Management for IT Services

Covers budgeting, accounting, charging/showback, cost optimization, ROI.
Includes simple planning, tracking, and reporting with a runnable demo.
"""

from __future__ import annotations
import sys
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import uuid
import asyncio

# Add parent directory so this can run standalone
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.service_value_system import Priority
except Exception:
    class Priority(Enum):
        LOW = "Low"; MEDIUM = "Medium"; HIGH = "High"; CRITICAL = "Critical"


class CostType(Enum):
    CAPEX = "CAPEX"
    OPEX = "OPEX"


@dataclass
class CostEntry:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service: str = "General"
    description: str = ""
    amount: Decimal = Decimal("0.00")
    cost_type: CostType = CostType.OPEX
    date: datetime = field(default_factory=datetime.now)


@dataclass
class Budget:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fiscal_year: int = datetime.now().year
    allocations: Dict[str, Decimal] = field(default_factory=dict)  # service -> amount

    def total(self) -> Decimal:
        return sum(self.allocations.values(), Decimal("0.00"))


@dataclass
class ChargeRate:
    service: str
    unit: str  # e.g. hour, GB, request
    rate: Decimal  # per unit


@dataclass
class Charge:
    service: str
    units: Decimal
    unit: str
    amount: Decimal
    consumer: str  # business unit / project


@dataclass
class Investment:
    name: str
    one_time_cost: Decimal
    annual_benefit: Decimal
    years: int

    def roi(self) -> Decimal:
        if self.one_time_cost == 0:
            return Decimal("0.00")
        total_benefit = self.annual_benefit * self.years
        return ((total_benefit - self.one_time_cost) / self.one_time_cost * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class FinancialManager:
    def __init__(self):
        self.budget = Budget(
            fiscal_year=datetime.now().year,
            allocations={
                "Customer Portal": Decimal("300000.00"),
                "Data Platform": Decimal("200000.00"),
                "Security": Decimal("150000.00"),
            },
        )
        self.actuals: List[CostEntry] = [
            CostEntry(service="Customer Portal", description="Cloud hosting", amount=Decimal("22000.00")),
            CostEntry(service="Customer Portal", description="Support", amount=Decimal("5000.00")),
            CostEntry(service="Data Platform", description="Storage", amount=Decimal("12000.00")),
            CostEntry(service="Security", description="MDR subscription", amount=Decimal("8000.00")),
        ]
        self.charge_rates: Dict[str, ChargeRate] = {
            "Customer Portal": ChargeRate("Customer Portal", unit="hour", rate=Decimal("0.50")),
            "Data Platform": ChargeRate("Data Platform", unit="GB", rate=Decimal("0.02")),
            "Security": ChargeRate("Security", unit="endpoint", rate=Decimal("1.00")),
        }

    def add_actual(self, entry: CostEntry):
        self.actuals.append(entry)

    def spend_by_service(self) -> Dict[str, Decimal]:
        totals: Dict[str, Decimal] = {}
        for a in self.actuals:
            totals[a.service] = totals.get(a.service, Decimal("0.00")) + a.amount
        return totals

    def budget_vs_actual(self) -> Dict[str, Dict[str, Decimal]]:
        report: Dict[str, Dict[str, Decimal]] = {}
        spend = self.spend_by_service()
        for service, allocated in self.budget.allocations.items():
            actual = spend.get(service, Decimal("0.00"))
            variance = allocated - actual
            report[service] = {
                "budget": allocated,
                "actual": actual,
                "variance": variance,
                "variance_pct": (variance / allocated * 100 if allocated else Decimal("0.00")).quantize(Decimal("0.01")),
            }
        return report

    def chargeback(self, consumption: Dict[str, Decimal], consumer: str) -> List[Charge]:
        invoices: List[Charge] = []
        for service, units in consumption.items():
            if service not in self.charge_rates:
                continue
            rate = self.charge_rates[service]
            amount = (rate.rate * units).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            invoices.append(Charge(service=service, units=units, unit=rate.unit, amount=amount, consumer=consumer))
        return invoices

    def optimization_opportunities(self) -> List[str]:
        suggestions: List[str] = []
        spend = self.spend_by_service()
        for service, actual in spend.items():
            budgeted = self.budget.allocations.get(service, Decimal("0.00"))
            if budgeted and actual > budgeted * Decimal("0.25"):
                suggestions.append(f"Review {service} reserved capacity or rightsizing")
            if service == "Data Platform" and actual > Decimal("10000.00"):
                suggestions.append("Enable storage tiering and compression")
        if spend.get("Security", Decimal("0.00")) < Decimal("5000.00"):
            suggestions.append("Assess underinvestment risk in Security controls")
        return suggestions

    def dashboard(self) -> Dict[str, Any]:
        bva = self.budget_vs_actual()
        total_budget = self.budget.total()
        total_actual = sum((r["actual"] for r in bva.values()), Decimal("0.00"))
        return {
            "total_budget": total_budget,
            "total_actual": total_actual,
            "variance": total_budget - total_actual,
            "services": bva,
            "optimization": self.optimization_opportunities(),
        }


async def main():
    print("💵 ITIL 4 Financial Management")
    print("=" * 50)
    fm = FinancialManager()

    print("\n📚 Budget vs Actual:")
    bva = fm.budget_vs_actual()
    for svc, vals in bva.items():
        print(f"  {svc}: Budget ${vals['budget']} | Actual ${vals['actual']} | Var ${vals['variance']} ({vals['variance_pct']}%)")

    print("\n🧾 Chargeback (Example):")
    charges = fm.chargeback({"Customer Portal": Decimal("120.0"), "Data Platform": Decimal("800.0")}, consumer="Project Phoenix")
    for c in charges:
        print(f"  {c.consumer} -> {c.service}: {c.units} {c.unit} x rate = ${c.amount}")

    print("\n📈 ROI Analysis:")
    invest = Investment(name="CI/CD Automation", one_time_cost=Decimal("50000.00"), annual_benefit=Decimal("30000.00"), years=3)
    print(f"  {invest.name}: ROI {invest.roi()}% over {invest.years} years")

    print("\n📊 Dashboard Summary:")
    dash = fm.dashboard()
    print(f"Total Budget ${dash['total_budget']} | Total Actual ${dash['total_actual']} | Variance ${dash['variance']}")
    if dash["optimization"]:
        print("Optimization Hints:")
        for s in dash["optimization"]:
            print(f"  - {s}")

    print("\n✅ Financial Management Demo Complete")


if __name__ == "__main__":
    asyncio.run(main())
