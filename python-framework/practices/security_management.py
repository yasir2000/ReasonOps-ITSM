"""
ITIL 4 Information Security Management Practice Implementation

This module provides security management capabilities including:
- Security policy and control management (CIA: confidentiality, integrity, availability)
- Vulnerability management lifecycle (discover, assess, remediate, verify)
- Security incident detection, triage, containment, eradication, and recovery
- Risk assessment and risk register with scoring (likelihood x impact)
- Compliance monitoring and audit findings (ISO 27001, SOC2, PCI DSS)
- Threat modeling and detection rules engine
- Reporting dashboards and KPIs
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
    # Fallback minimal enums to keep demo runnable without the full framework
    class Priority(Enum):
        LOW = "Low"; MEDIUM = "Medium"; HIGH = "High"; CRITICAL = "Critical"
    class Status(Enum):
        NEW = "New"; IN_PROGRESS = "In Progress"; RESOLVED = "Resolved"; CLOSED = "Closed"
    class Impact(Enum):
        LOW = "Low"; MEDIUM = "Medium"; HIGH = "High"; CRITICAL = "Critical"
    class Urgency(Enum):
        LOW = "Low"; MEDIUM = "Medium"; HIGH = "High"; CRITICAL = "Critical"


class SecuritySeverity(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ThreatType(Enum):
    MALWARE = "Malware"
    PHISHING = "Phishing"
    RANSOMWARE = "Ransomware"
    DATA_LEAK = "Data Leak"
    PRIVILEGE_ABUSE = "Privilege Abuse"
    MISCONFIGURATION = "Misconfiguration"
    VULNERABILITY = "Vulnerability"
    DDOS = "DDoS"
    SUPPLY_CHAIN = "Supply Chain"


class ControlType(Enum):
    PREVENTIVE = "Preventive"
    DETECTIVE = "Detective"
    CORRECTIVE = "Corrective"
    DETERRENT = "Deterrent"
    COMPENSATING = "Compensating"


class ComplianceStandard(Enum):
    ISO27001 = "ISO 27001"
    SOC2 = "SOC 2"
    PCI_DSS = "PCI DSS"
    HIPAA = "HIPAA"
    GDPR = "GDPR"


@dataclass
class SecurityControl:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    control_type: ControlType = ControlType.PREVENTIVE
    owner: str = "Security"
    implemented: bool = False
    effectiveness: float = 0.0  # 0-1 scale
    related_standards: List[ComplianceStandard] = field(default_factory=list)
    related_assets: List[str] = field(default_factory=list)
    last_test_date: Optional[datetime] = None
    next_test_date: Optional[datetime] = None


@dataclass
class Vulnerability:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    cve: Optional[str] = None
    severity: SecuritySeverity = SecuritySeverity.MEDIUM
    cvss_score: float = 5.0
    affected_asset: Optional[str] = None
    discovered_date: datetime = field(default_factory=datetime.now)
    remediation_due: Optional[datetime] = None
    status: Status = Status.NEW
    remediation_plan: Optional[str] = None


@dataclass
class VulnerabilityScanResult:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    scan_tool: str = "Internal Scanner"
    target: str = ""
    scan_date: datetime = field(default_factory=datetime.now)
    findings: List[Vulnerability] = field(default_factory=list)


@dataclass
class SecurityIncident:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    threat_type: ThreatType = ThreatType.MISCONFIGURATION
    severity: SecuritySeverity = SecuritySeverity.MEDIUM
    impact: Impact = Impact.MEDIUM
    urgency: Urgency = Urgency.MEDIUM
    status: Status = Status.NEW
    detected_at: datetime = field(default_factory=datetime.now)
    contained_at: Optional[datetime] = None
    eradicated_at: Optional[datetime] = None
    recovered_at: Optional[datetime] = None
    affected_assets: List[str] = field(default_factory=list)
    related_vulnerabilities: List[str] = field(default_factory=list)
    root_cause: Optional[str] = None
    lessons_learned: List[str] = field(default_factory=list)


@dataclass
class RiskAssessment:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    asset_id: str = ""
    asset_name: str = ""
    threat: ThreatType = ThreatType.MISCONFIGURATION
    likelihood: int = 3  # 1-5
    impact: int = 3      # 1-5
    inherent_risk: int = 9
    residual_risk: int = 6
    controls_applied: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    assessed_at: datetime = field(default_factory=datetime.now)

    def calculate_scores(self, control_effectiveness: float = 0.0):
        self.inherent_risk = self.likelihood * self.impact
        # Residual = inherent reduced by control effectiveness
        self.residual_risk = max(1, int(round(self.inherent_risk * (1 - min(1.0, control_effectiveness)))))


@dataclass
class ComplianceFinding:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    standard: ComplianceStandard = ComplianceStandard.ISO27001
    control_reference: str = ""
    description: str = ""
    severity: SecuritySeverity = SecuritySeverity.MEDIUM
    status: Status = Status.NEW
    remediation_owner: str = "Security"
    due_date: Optional[datetime] = None


class SecurityMonitoringEngine:
    """Simple rule-based detection engine for security events."""
    def __init__(self):
        self.rules: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)

    def add_rule(self, name: str, condition, action):
        self.rules.append({"name": name, "condition": condition, "action": action})

    def evaluate_event(self, event: Dict[str, Any]) -> List[str]:
        triggered = []
        for rule in self.rules:
            try:
                if rule["condition"](event):
                    rule["action"](event)
                    triggered.append(rule["name"])
            except Exception as e:
                self.logger.exception(f"Security rule '{rule['name']}' failed: {e}")
        return triggered


class SecurityManager:
    """Main Information Security Management system."""
    def __init__(self):
        self.controls: Dict[str, SecurityControl] = {}
        self.vulnerabilities: Dict[str, Vulnerability] = {}
        self.incidents: Dict[str, SecurityIncident] = {}
        self.risks: Dict[str, RiskAssessment] = {}
        self.compliance_findings: Dict[str, ComplianceFinding] = {}
        self.scan_results: List[VulnerabilityScanResult] = []
        self.monitor = SecurityMonitoringEngine()
        self.logger = logging.getLogger(__name__)

        self._init_sample_data()
        self._init_default_rules()

    def _init_sample_data(self):
        # Controls
        c1 = SecurityControl(
            name="Multi-Factor Authentication",
            description="Require MFA for privileged access",
            control_type=ControlType.PREVENTIVE,
            implemented=True,
            effectiveness=0.7,
            related_standards=[ComplianceStandard.ISO27001, ComplianceStandard.SOC2],
            last_test_date=datetime.now() - timedelta(days=60),
            next_test_date=datetime.now() + timedelta(days=30)
        )
        c2 = SecurityControl(
            name="Endpoint EDR",
            description="Endpoint detection and response agent deployed",
            control_type=ControlType.DETECTIVE,
            implemented=True,
            effectiveness=0.6,
            related_standards=[ComplianceStandard.SOC2, ComplianceStandard.PCI_DSS]
        )
        c3 = SecurityControl(
            name="Offsite Backups",
            description="Daily encrypted backups to offsite location",
            control_type=ControlType.CORRECTIVE,
            implemented=True,
            effectiveness=0.8,
            related_standards=[ComplianceStandard.ISO27001]
        )
        for ctrl in (c1, c2, c3):
            self.controls[ctrl.id] = ctrl

        # Example vulnerability
        v1 = Vulnerability(
            title="OpenSSL Buffer Overflow",
            cve="CVE-2023-XYZ",
            severity=SecuritySeverity.HIGH,
            cvss_score=8.1,
            affected_asset="SRV-001",
            remediation_due=datetime.now() + timedelta(days=14),
            remediation_plan="Patch OpenSSL to latest version"
        )
        self.vulnerabilities[v1.id] = v1

        # Example risk assessment
        r1 = RiskAssessment(
            asset_id="SRV-001",
            asset_name="Production Web Server",
            threat=ThreatType.RANSOMWARE,
            likelihood=3,
            impact=5,
            controls_applied=[c2.id, c3.id],
            recommendations=["Improve EDR coverage", "Test restore procedures quarterly"]
        )
        r1.calculate_scores(control_effectiveness=0.6)
        self.risks[r1.id] = r1

        # Example compliance finding
        cf1 = ComplianceFinding(
            standard=ComplianceStandard.ISO27001,
            control_reference="A.12.6 - Technical Vulnerability Management",
            description="Missing SLA for critical patching",
            severity=SecuritySeverity.MEDIUM,
            due_date=datetime.now() + timedelta(days=30)
        )
        self.compliance_findings[cf1.id] = cf1

    def _init_default_rules(self):
        # High error rate with auth events -> potential credential stuffing
        self.monitor.add_rule(
            name="Credential Stuffing Suspected",
            condition=lambda e: e.get("event_type") == "auth_failure" and e.get("failures", 0) > 50,
            action=lambda e: self.create_incident(
                title="Possible credential stuffing",
                description=f"High auth failures from IP {e.get('source_ip')}",
                threat_type=ThreatType.PRIVILEGE_ABUSE,
                severity=SecuritySeverity.HIGH,
                affected_assets=[e.get("target_service", "Unknown")]
            )
        )
        # Data exfil suspected when outbound traffic spikes and unusual destinations
        self.monitor.add_rule(
            name="Data Exfiltration Suspected",
            condition=lambda e: e.get("event_type") == "net_egress" and e.get("gb_out", 0) > 50 and e.get("dest_country") not in ("US", "EU"),
            action=lambda e: self.create_incident(
                title="Possible data exfiltration",
                description=f"{e.get('gb_out')}GB outbound to {e.get('dest_country')}",
                threat_type=ThreatType.DATA_LEAK,
                severity=SecuritySeverity.CRITICAL,
                affected_assets=[e.get("hostname", "Unknown")]
            )
        )

    # Core functions
    def create_incident(self, title: str, description: str, threat_type: ThreatType,
                        severity: SecuritySeverity, affected_assets: Optional[List[str]] = None) -> str:
        incident = SecurityIncident(
            title=title,
            description=description,
            threat_type=threat_type,
            severity=severity,
            impact=Impact.CRITICAL if severity == SecuritySeverity.CRITICAL else Impact.HIGH if severity == SecuritySeverity.HIGH else Impact.MEDIUM,
            urgency=Urgency.CRITICAL if severity == SecuritySeverity.CRITICAL else Urgency.HIGH if severity == SecuritySeverity.HIGH else Urgency.MEDIUM,
            status=Status.NEW,
            affected_assets=affected_assets or []
        )
        self.incidents[incident.id] = incident
        return incident.id

    def update_incident_status(self, incident_id: str, status: Status):
        inc = self.incidents.get(incident_id)
        if not inc:
            return False
        inc.status = status
        now = datetime.now()
        if status == Status.IN_PROGRESS and not inc.contained_at:
            inc.contained_at = now
        if status == Status.RESOLVED and not inc.eradicated_at:
            inc.eradicated_at = now
        if status == Status.CLOSED and not inc.recovered_at:
            inc.recovered_at = now
        return True

    def run_vulnerability_scan(self, target: str) -> VulnerabilityScanResult:
        # Mock scanning
        finding = Vulnerability(
            title="Outdated TLS configuration",
            severity=SecuritySeverity.MEDIUM,
            cvss_score=6.5,
            affected_asset=target,
            remediation_due=datetime.now() + timedelta(days=21),
            remediation_plan="Disable TLS 1.0/1.1 and enable TLS 1.2+"
        )
        self.vulnerabilities[finding.id] = finding
        result = VulnerabilityScanResult(target=target, findings=[finding])
        self.scan_results.append(result)
        return result

    def calculate_overall_risk(self) -> Dict[str, Any]:
        risks = list(self.risks.values())
        if not risks:
            return {"score": 0, "high_risks": 0, "critical_risks": 0}
        avg_residual = sum(r.residual_risk for r in risks) / len(risks)
        high = len([r for r in risks if r.residual_risk >= 12])
        critical = len([r for r in risks if r.residual_risk >= 16])
        return {"score": avg_residual, "high_risks": high, "critical_risks": critical}

    def evaluate_controls_effectiveness(self) -> float:
        if not self.controls:
            return 0.0
        implemented = [c.effectiveness for c in self.controls.values() if c.implemented]
        return sum(implemented) / max(1, len(implemented))

    def get_compliance_summary(self) -> Dict[str, Any]:
        findings = list(self.compliance_findings.values())
        return {
            "open_findings": len([f for f in findings if f.status in (Status.NEW, Status.IN_PROGRESS)]),
            "overdue": len([f for f in findings if f.due_date and f.due_date < datetime.now() and f.status != Status.CLOSED]),
            "by_standard": self._findings_by_standard(findings)
        }

    def _findings_by_standard(self, findings: List[ComplianceFinding]) -> Dict[str, int]:
        counts: Dict[str, int] = defaultdict(int)
        for f in findings:
            counts[f.standard.value] += 1
        return dict(counts)

    def triage_vulnerabilities(self) -> Dict[str, List[Vulnerability]]:
        buckets: Dict[str, List[Vulnerability]] = {"Critical": [], "High": [], "Medium": [], "Low": []}
        for v in self.vulnerabilities.values():
            buckets[v.severity.value].append(v)
        return buckets

    def generate_security_report(self) -> Dict[str, Any]:
        risk = self.calculate_overall_risk()
        control_eff = self.evaluate_controls_effectiveness()
        vuln_buckets = self.triage_vulnerabilities()
        compliance = self.get_compliance_summary()
        return {
            "generated": datetime.now().isoformat(),
            "risk": risk,
            "control_effectiveness": round(control_eff * 100, 1),
            "vulnerabilities": {k: len(v) for k, v in vuln_buckets.items()},
            "incidents_open": len([i for i in self.incidents.values() if i.status != Status.CLOSED]),
            "compliance": compliance
        }

    def get_dashboard(self) -> Dict[str, Any]:
        report = self.generate_security_report()
        top_vulns = sorted(self.vulnerabilities.values(), key=lambda v: (-v.cvss_score, v.discovered_date))[:5]
        recent_incidents = sorted(self.incidents.values(), key=lambda i: i.detected_at, reverse=True)[:5]
        return {
            "summary": report,
            "top_vulnerabilities": [
                {
                    "title": v.title,
                    "cve": v.cve,
                    "severity": v.severity.value,
                    "cvss": v.cvss_score,
                    "asset": v.affected_asset,
                    "due_in_days": (v.remediation_due - datetime.now()).days if v.remediation_due else None
                } for v in top_vulns
            ],
            "recent_incidents": [
                {
                    "title": i.title,
                    "severity": i.severity.value,
                    "status": i.status.value,
                    "threat": i.threat_type.value,
                    "detected_at": i.detected_at.isoformat()
                } for i in recent_incidents
            ]
        }

    def handle_event(self, event: Dict[str, Any]) -> List[str]:
        return self.monitor.evaluate_event(event)


async def main():
    print("🔐 ITIL 4 Information Security Management")
    print("=" * 50)
    sm = SecurityManager()

    # Show summary
    summary = sm.generate_security_report()
    print("\n📊 Security Summary:")
    print(f"Residual Risk Score: {summary['risk']['score']:.1f}")
    print(f"Control Effectiveness: {summary['control_effectiveness']:.1f}%")
    print(f"Open Incidents: {summary['incidents_open']}")
    print(f"Open Compliance Findings: {summary['compliance']['open_findings']}")

    # Run a vulnerability scan
    print("\n🗺️ Vulnerability Scan:")
    scan = sm.run_vulnerability_scan(target="SRV-002")
    print(f"Scanner: {scan.scan_tool} | Target: {scan.target} | Findings: {len(scan.findings)}")

    # Triage vulnerabilities
    print("\n🚦 Vulnerability Triage:")
    triage = sm.triage_vulnerabilities()
    for sev in ("Critical", "High", "Medium", "Low"):
        print(f"  {sev}: {len(triage.get(sev, []))}")

    # Simulate detection events
    print("\n🛡️ Detection Engine:")
    triggers = sm.handle_event({"event_type": "auth_failure", "failures": 75, "source_ip": "203.0.113.10", "target_service": "Customer Portal"})
    print(f"Triggered Rules: {', '.join(triggers) if triggers else 'None'}")

    # Incident overview
    open_inc = [i for i in sm.incidents.values() if i.status != Status.CLOSED]
    print(f"Open Security Incidents: {len(open_inc)}")
    if open_inc:
        inc = open_inc[0]
        print(f"  - {inc.title} | {inc.severity.value} | {inc.status.value}")

    # Dashboard snapshot
    print("\n📈 Security Dashboard Snapshot:")
    dash = sm.get_dashboard()
    print(f"Top Vulnerabilities Listed: {len(dash['top_vulnerabilities'])}")
    print(f"Recent Incidents Listed: {len(dash['recent_incidents'])}")

    print("\n✅ Security Management Demo Complete")


if __name__ == "__main__":
    asyncio.run(main())
