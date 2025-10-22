"""
ITIL 4 Service Level Management Practice Implementation

This module provides comprehensive service level management capabilities including:
- Service Level Agreements (SLA) management and monitoring
- Operational Level Agreements (OLA) tracking
- Underpinning Contracts (UC) management
- Service level reporting and analytics
- SLA breach detection and alerting
- Performance trend analysis
- Service quality metrics and KPIs
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
import asyncio
from collections import defaultdict, deque
import statistics

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.service_value_system import Priority, Status, Impact, Urgency
# Safe import to support environments where IncidentManager is defined as IncidentManagement
try:
    from practices.incident_management import Incident, IncidentManagement as IncidentManager
except Exception:  # pragma: no cover - fallback types for standalone runs
    Incident = None  # type: ignore
    class IncidentManager:  # type: ignore
        async def create_incident(self, *args, **kwargs):
            return None


class AgreementType(Enum):
    """Types of service level agreements"""
    SLA = "Service Level Agreement"
    OLA = "Operational Level Agreement"
    UC = "Underpinning Contract"


class MetricType(Enum):
    """Types of service level metrics"""
    AVAILABILITY = "Availability"
    RESPONSE_TIME = "Response Time"
    RESOLUTION_TIME = "Resolution Time"
    THROUGHPUT = "Throughput"
    ERROR_RATE = "Error Rate"
    CAPACITY_UTILIZATION = "Capacity Utilization"
    CUSTOMER_SATISFACTION = "Customer Satisfaction"
    FIRST_CALL_RESOLUTION = "First Call Resolution"
    MEAN_TIME_TO_REPAIR = "Mean Time To Repair"
    MEAN_TIME_BETWEEN_FAILURES = "Mean Time Between Failures"


class AlertSeverity(Enum):
    """Severity levels for SLA alerts"""
    INFO = "Information"
    WARNING = "Warning"
    CRITICAL = "Critical"
    BREACH = "Breach"


class ReportingPeriod(Enum):
    """Reporting periods for SLA metrics"""
    HOURLY = "Hourly"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    ANNUALLY = "Annually"


@dataclass
class ServiceLevelTarget:
    """Represents a service level target within an agreement"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    metric_type: MetricType = MetricType.AVAILABILITY
    target_value: float = 0.0
    target_operator: str = ">="  # >=, <=, =, >, <
    unit: str = "%"
    measurement_period: str = "Monthly"
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    measurement_method: str = ""
    exclusions: List[str] = field(default_factory=list)
    penalty_clause: Optional[str] = None
    
    def is_target_met(self, actual_value: float) -> bool:
        """Check if the target is met by the actual value"""
        if self.target_operator == ">=":
            return actual_value >= self.target_value
        elif self.target_operator == "<=":
            return actual_value <= self.target_value
        elif self.target_operator == "=":
            return abs(actual_value - self.target_value) < 0.001  # Small tolerance for float comparison
        elif self.target_operator == ">":
            return actual_value > self.target_value
        elif self.target_operator == "<":
            return actual_value < self.target_value
        return False
    
    def get_alert_severity(self, actual_value: float) -> AlertSeverity:
        """Determine alert severity based on actual value"""
        if not self.is_target_met(actual_value):
            return AlertSeverity.BREACH
        
        if self.critical_threshold and self.target_operator == ">=" and actual_value <= self.critical_threshold:
            return AlertSeverity.CRITICAL
        elif self.critical_threshold and self.target_operator == "<=" and actual_value >= self.critical_threshold:
            return AlertSeverity.CRITICAL
        
        if self.warning_threshold and self.target_operator == ">=" and actual_value <= self.warning_threshold:
            return AlertSeverity.WARNING
        elif self.warning_threshold and self.target_operator == "<=" and actual_value >= self.warning_threshold:
            return AlertSeverity.WARNING
        
        return AlertSeverity.INFO


@dataclass
class ServiceLevelAgreement:
    """Represents a Service Level Agreement"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    agreement_type: AgreementType = AgreementType.SLA
    service_name: str = ""
    customer: str = ""
    provider: str = ""
    
    # Agreement details
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    review_date: Optional[datetime] = None
    status: str = "Active"
    
    # Service level targets
    targets: List[ServiceLevelTarget] = field(default_factory=list)
    
    # Business details
    business_hours: Dict[str, Any] = field(default_factory=lambda: {
        "monday": {"start": "09:00", "end": "17:00"},
        "tuesday": {"start": "09:00", "end": "17:00"},
        "wednesday": {"start": "09:00", "end": "17:00"},
        "thursday": {"start": "09:00", "end": "17:00"},
        "friday": {"start": "09:00", "end": "17:00"},
        "saturday": {"start": "closed", "end": "closed"},
        "sunday": {"start": "closed", "end": "closed"}
    })
    
    escalation_contacts: List[Dict[str, str]] = field(default_factory=list)
    reporting_schedule: Dict[str, str] = field(default_factory=lambda: {
        "frequency": "Monthly",
        "day_of_month": "1",
        "recipients": []
    })
    
    # Performance tracking
    created_date: datetime = field(default_factory=datetime.now)
    last_reviewed: Optional[datetime] = None
    
    def add_target(self, target: ServiceLevelTarget):
        """Add a service level target to the agreement"""
        self.targets.append(target)
    
    def remove_target(self, target_id: str):
        """Remove a service level target from the agreement"""
        self.targets = [t for t in self.targets if t.id != target_id]
    
    def get_target(self, target_id: str) -> Optional[ServiceLevelTarget]:
        """Get a specific target by ID"""
        return next((t for t in self.targets if t.id == target_id), None)
    
    def is_active(self) -> bool:
        """Check if the agreement is currently active"""
        now = datetime.now()
        return (self.status == "Active" and 
                self.start_date <= now and 
                (self.end_date is None or self.end_date >= now))


@dataclass
class ServiceLevelMeasurement:
    """Represents a service level measurement"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agreement_id: str = ""
    target_id: str = ""
    measurement_date: datetime = field(default_factory=datetime.now)
    measurement_period_start: datetime = field(default_factory=datetime.now)
    measurement_period_end: datetime = field(default_factory=datetime.now)
    actual_value: float = 0.0
    target_value: float = 0.0
    target_met: bool = False
    alert_severity: AlertSeverity = AlertSeverity.INFO
    data_points: int = 0
    raw_data: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    
    def calculate_variance(self) -> float:
        """Calculate variance from target"""
        return self.actual_value - self.target_value


@dataclass
class SLABreach:
    """Represents an SLA breach incident"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agreement_id: str = ""
    target_id: str = ""
    measurement_id: str = ""
    breach_date: datetime = field(default_factory=datetime.now)
    severity: AlertSeverity = AlertSeverity.BREACH
    actual_value: float = 0.0
    target_value: float = 0.0
    variance: float = 0.0
    impact_assessment: str = ""
    root_cause: str = ""
    corrective_actions: List[str] = field(default_factory=list)
    status: str = "Open"  # Open, Investigating, Resolved, Closed
    assigned_to: Optional[str] = None
    resolution_date: Optional[datetime] = None
    incident_id: Optional[str] = None  # Link to related incident


class ServiceLevelReporter:
    """Generates service level reports and analytics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_sla_report(self, agreement: ServiceLevelAgreement, 
                           measurements: List[ServiceLevelMeasurement],
                           period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Generate comprehensive SLA report"""
        
        # Filter measurements for the reporting period
        period_measurements = [
            m for m in measurements 
            if (m.agreement_id == agreement.id and
                period_start <= m.measurement_date <= period_end)
        ]
        
        report = {
            "agreement_id": agreement.id,
            "agreement_name": agreement.name,
            "service_name": agreement.service_name,
            "customer": agreement.customer,
            "provider": agreement.provider,
            "reporting_period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat()
            },
            "generated_date": datetime.now().isoformat(),
            "summary": {
                "total_targets": len(agreement.targets),
                "targets_met": 0,
                "targets_breached": 0,
                "overall_compliance": 0.0
            },
            "target_performance": [],
            "trends": {},
            "breaches": [],
            "recommendations": []
        }
        
        # Analyze each target
        for target in agreement.targets:
            target_measurements = [
                m for m in period_measurements if m.target_id == target.id
            ]
            
            if not target_measurements:
                continue
            
            # Calculate target performance
            target_performance = self._analyze_target_performance(target, target_measurements)
            report["target_performance"].append(target_performance)
            
            # Update summary
            if target_performance["compliance_percentage"] >= 100:
                report["summary"]["targets_met"] += 1
            else:
                report["summary"]["targets_breached"] += 1
        
        # Calculate overall compliance
        if report["summary"]["total_targets"] > 0:
            report["summary"]["overall_compliance"] = (
                report["summary"]["targets_met"] / 
                report["summary"]["total_targets"] * 100
            )
        
        # Generate trends
        report["trends"] = self._analyze_trends(period_measurements)
        
        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(report)
        
        return report
    
    def _analyze_target_performance(self, target: ServiceLevelTarget, 
                                   measurements: List[ServiceLevelMeasurement]) -> Dict[str, Any]:
        """Analyze performance for a specific target"""
        
        if not measurements:
            return {
                "target_id": target.id,
                "target_name": target.name,
                "metric_type": target.metric_type.value,
                "target_value": target.target_value,
                "unit": target.unit,
                "measurements_count": 0,
                "average_value": 0,
                "best_value": 0,
                "worst_value": 0,
                "compliance_percentage": 0,
                "breach_count": 0
            }
        
        # Calculate statistics
        values = [m.actual_value for m in measurements]
        met_count = sum(1 for m in measurements if m.target_met)
        breach_count = len(measurements) - met_count
        
        performance = {
            "target_id": target.id,
            "target_name": target.name,
            "metric_type": target.metric_type.value,
            "target_value": target.target_value,
            "target_operator": target.target_operator,
            "unit": target.unit,
            "measurements_count": len(measurements),
            "average_value": statistics.mean(values),
            "median_value": statistics.median(values),
            "best_value": max(values) if target.target_operator in [">=", ">"] else min(values),
            "worst_value": min(values) if target.target_operator in [">=", ">"] else max(values),
            "standard_deviation": statistics.stdev(values) if len(values) > 1 else 0,
            "compliance_percentage": (met_count / len(measurements)) * 100,
            "breach_count": breach_count,
            "trend": self._calculate_trend(values)
        }
        
        return performance
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a series of values"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear trend calculation
        n = len(values)
        x = list(range(n))
        
        # Calculate slope using least squares
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        if slope > 0.1:
            return "improving"
        elif slope < -0.1:
            return "declining"
        else:
            return "stable"
    
    def _analyze_trends(self, measurements: List[ServiceLevelMeasurement]) -> Dict[str, Any]:
        """Analyze trends across all measurements"""
        
        if not measurements:
            return {}
        
        # Group measurements by target
        target_groups = defaultdict(list)
        for measurement in measurements:
            target_groups[measurement.target_id].append(measurement)
        
        trends = {}
        for target_id, target_measurements in target_groups.items():
            values = [m.actual_value for m in sorted(target_measurements, key=lambda x: x.measurement_date)]
            trends[target_id] = {
                "trend_direction": self._calculate_trend(values),
                "measurement_count": len(values),
                "date_range": {
                    "start": min(m.measurement_date for m in target_measurements).isoformat(),
                    "end": max(m.measurement_date for m in target_measurements).isoformat()
                }
            }
        
        return trends
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on report analysis"""
        
        recommendations = []
        
        # Overall compliance recommendations
        overall_compliance = report["summary"]["overall_compliance"]
        if overall_compliance < 95:
            recommendations.append(
                f"Overall SLA compliance is {overall_compliance:.1f}%. "
                "Consider reviewing service delivery processes and resource allocation."
            )
        
        # Target-specific recommendations
        for target_perf in report["target_performance"]:
            compliance = target_perf["compliance_percentage"]
            trend = target_perf.get("trend", "unknown")
            
            if compliance < 100:
                recommendations.append(
                    f"Target '{target_perf['target_name']}' has {target_perf['breach_count']} breaches. "
                    f"Review processes and consider capacity improvements."
                )
            
            if trend == "declining":
                recommendations.append(
                    f"Target '{target_perf['target_name']}' shows declining trend. "
                    "Investigate root causes and implement preventive measures."
                )
        
        # Breach-based recommendations
        breach_count = report["summary"]["targets_breached"]
        if breach_count > 0:
            recommendations.append(
                f"Implement proactive monitoring and alerting for {breach_count} breached targets."
            )
        
        return recommendations


class ServiceLevelManager:
    """Main service level management system"""
    
    def __init__(self, incident_manager: Optional[IncidentManager] = None):
        self.agreements: Dict[str, ServiceLevelAgreement] = {}
        self.measurements: List[ServiceLevelMeasurement] = []
        self.breaches: List[SLABreach] = []
        self.reporter = ServiceLevelReporter()
        self.incident_manager = incident_manager
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.stats = {
            "total_agreements": 0,
            "active_agreements": 0,
            "total_measurements": 0,
            "total_breaches": 0,
            "average_compliance": 0.0
        }
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample SLA data"""
        
        # Sample SLA for Customer Portal
        portal_sla = ServiceLevelAgreement(
            name="Customer Portal SLA",
            description="Service level agreement for customer-facing web portal",
            service_name="Customer Portal",
            customer="Business Units",
            provider="IT Operations",
            start_date=datetime.now() - timedelta(days=90),
            end_date=datetime.now() + timedelta(days=275)
        )
        
        # Add targets
        availability_target = ServiceLevelTarget(
            name="System Availability",
            description="Portal must be available 99.5% of the time during business hours",
            metric_type=MetricType.AVAILABILITY,
            target_value=99.5,
            target_operator=">=",
            unit="%",
            measurement_period="Monthly",
            warning_threshold=99.0,
            critical_threshold=98.5,
            measurement_method="Synthetic monitoring every 5 minutes"
        )
        
        response_time_target = ServiceLevelTarget(
            name="Response Time",
            description="Portal pages must load within 3 seconds",
            metric_type=MetricType.RESPONSE_TIME,
            target_value=3.0,
            target_operator="<=",
            unit="seconds",
            measurement_period="Daily",
            warning_threshold=4.0,
            critical_threshold=5.0,
            measurement_method="End-user monitoring from multiple locations"
        )
        
        incident_response_target = ServiceLevelTarget(
            name="Incident Response Time",
            description="P1 incidents must be acknowledged within 15 minutes",
            metric_type=MetricType.RESPONSE_TIME,
            target_value=15.0,
            target_operator="<=",
            unit="minutes",
            measurement_period="Monthly",
            warning_threshold=20.0,
            critical_threshold=30.0,
            measurement_method="Time from incident creation to first response"
        )
        
        portal_sla.add_target(availability_target)
        portal_sla.add_target(response_time_target)
        portal_sla.add_target(incident_response_target)
        
        self.create_agreement(portal_sla)
        
        # Generate some sample measurements
        self._generate_sample_measurements(portal_sla.id)
    
    def _generate_sample_measurements(self, agreement_id: str):
        """Generate sample measurements for demonstration"""
        
        agreement = self.agreements.get(agreement_id)
        if not agreement:
            return
        
        # Generate measurements for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        for target in agreement.targets:
            current_date = start_date
            
            while current_date <= end_date:
                # Generate realistic sample values
                if target.metric_type == MetricType.AVAILABILITY:
                    # Availability usually high with occasional dips
                    base_value = 99.7
                    variation = (hash(str(current_date)) % 100) / 1000  # Small random variation
                    actual_value = base_value + variation
                    if (hash(str(current_date)) % 20) == 0:  # Occasional outage
                        actual_value = 98.5 + variation
                
                elif target.metric_type == MetricType.RESPONSE_TIME:
                    # Response time usually good with occasional spikes
                    base_value = 2.5
                    variation = (hash(str(current_date)) % 50) / 100  # Random variation
                    actual_value = base_value + variation
                    if (hash(str(current_date)) % 15) == 0:  # Occasional spike
                        actual_value = 4.5 + variation
                
                else:  # Incident response time
                    base_value = 12.0
                    variation = (hash(str(current_date)) % 30) / 10  # Random variation
                    actual_value = base_value + variation
                    if (hash(str(current_date)) % 25) == 0:  # Occasional delay
                        actual_value = 25.0 + variation
                
                measurement = ServiceLevelMeasurement(
                    agreement_id=agreement_id,
                    target_id=target.id,
                    measurement_date=current_date,
                    measurement_period_start=current_date,
                    measurement_period_end=current_date + timedelta(hours=1),
                    actual_value=actual_value,
                    target_value=target.target_value,
                    target_met=target.is_target_met(actual_value),
                    alert_severity=target.get_alert_severity(actual_value),
                    data_points=1
                )
                
                self.record_measurement(measurement)
                
                # Check for breach
                if not measurement.target_met:
                    self._create_breach(measurement)
                
                current_date += timedelta(days=1)
    
    def create_agreement(self, agreement: ServiceLevelAgreement) -> str:
        """Create a new service level agreement"""
        
        self.agreements[agreement.id] = agreement
        self.stats["total_agreements"] += 1
        
        if agreement.is_active():
            self.stats["active_agreements"] += 1
        
        self.logger.info(f"Created SLA {agreement.id}: {agreement.name}")
        return agreement.id
    
    def get_agreement(self, agreement_id: str) -> Optional[ServiceLevelAgreement]:
        """Get an agreement by ID"""
        return self.agreements.get(agreement_id)
    
    def update_agreement(self, agreement_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing agreement"""
        
        agreement = self.agreements.get(agreement_id)
        if not agreement:
            return False
        
        # Update basic fields
        for key, value in updates.items():
            if hasattr(agreement, key):
                setattr(agreement, key, value)
        
        self.logger.info(f"Updated SLA {agreement_id}")
        return True
    
    def record_measurement(self, measurement: ServiceLevelMeasurement) -> str:
        """Record a service level measurement"""
        
        self.measurements.append(measurement)
        self.stats["total_measurements"] += 1
        
        # Update compliance statistics
        self._update_compliance_stats()
        
        self.logger.debug(f"Recorded measurement for agreement {measurement.agreement_id}")
        return measurement.id
    
    def _create_breach(self, measurement: ServiceLevelMeasurement):
        """Create a breach record for a failed measurement"""
        
        breach = SLABreach(
            agreement_id=measurement.agreement_id,
            target_id=measurement.target_id,
            measurement_id=measurement.id,
            breach_date=measurement.measurement_date,
            severity=measurement.alert_severity,
            actual_value=measurement.actual_value,
            target_value=measurement.target_value,
            variance=measurement.calculate_variance()
        )
        
        self.breaches.append(breach)
        self.stats["total_breaches"] += 1
        
        # Create incident if incident manager is available
        if self.incident_manager and measurement.alert_severity == AlertSeverity.BREACH:
            asyncio.create_task(self._create_breach_incident(breach))
        
        self.logger.warning(f"SLA breach detected: {breach.id}")
    
    async def _create_breach_incident(self, breach: SLABreach):
        """Create an incident for an SLA breach"""
        
        try:
            agreement = self.agreements.get(breach.agreement_id)
            if not agreement:
                return
            
            target = agreement.get_target(breach.target_id)
            if not target:
                return
            
            incident_data = {
                "title": f"SLA Breach: {target.name} for {agreement.name}",
                "description": f"Service level breach detected\n\n"
                              f"Agreement: {agreement.name}\n"
                              f"Target: {target.name}\n"
                              f"Expected: {target.target_operator} {target.target_value} {target.unit}\n"
                              f"Actual: {breach.actual_value} {target.unit}\n"
                              f"Variance: {breach.variance} {target.unit}\n"
                              f"Breach Time: {breach.breach_date.isoformat()}",
                "priority": "P2 - High",
                "impact": "Medium",
                "urgency": "High",
                "category": "Service Level",
                "subcategory": "SLA Breach",
                "reporter": "Service Level Manager",
                "source": "SLA Monitoring"
            }
            
            incident = await self.incident_manager.create_incident(incident_data)
            breach.incident_id = incident.id
            
            self.logger.info(f"Created incident {incident.id} for SLA breach {breach.id}")
            
        except Exception as e:
            self.logger.error(f"Failed to create incident for SLA breach: {e}")
    
    def get_measurements(self, agreement_id: str, target_id: Optional[str] = None,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> List[ServiceLevelMeasurement]:
        """Get measurements for an agreement with optional filters"""
        
        measurements = [m for m in self.measurements if m.agreement_id == agreement_id]
        
        if target_id:
            measurements = [m for m in measurements if m.target_id == target_id]
        
        if start_date:
            measurements = [m for m in measurements if m.measurement_date >= start_date]
        
        if end_date:
            measurements = [m for m in measurements if m.measurement_date <= end_date]
        
        return measurements
    
    def get_breaches(self, agreement_id: Optional[str] = None,
                    severity: Optional[AlertSeverity] = None,
                    status: Optional[str] = None) -> List[SLABreach]:
        """Get breaches with optional filters"""
        
        breaches = self.breaches.copy()
        
        if agreement_id:
            breaches = [b for b in breaches if b.agreement_id == agreement_id]
        
        if severity:
            breaches = [b for b in breaches if b.severity == severity]
        
        if status:
            breaches = [b for b in breaches if b.status == status]
        
        return breaches
    
    def generate_report(self, agreement_id: str, period: ReportingPeriod = ReportingPeriod.MONTHLY) -> Dict[str, Any]:
        """Generate a service level report"""
        
        agreement = self.agreements.get(agreement_id)
        if not agreement:
            return {"error": "Agreement not found"}
        
        # Determine reporting period
        end_date = datetime.now()
        
        if period == ReportingPeriod.DAILY:
            start_date = end_date - timedelta(days=1)
        elif period == ReportingPeriod.WEEKLY:
            start_date = end_date - timedelta(weeks=1)
        elif period == ReportingPeriod.MONTHLY:
            start_date = end_date - timedelta(days=30)  # Approximate month
        elif period == ReportingPeriod.QUARTERLY:
            start_date = end_date - timedelta(days=90)  # Approximate quarter
        else:
            start_date = end_date - timedelta(days=365)  # Annual
        
        # Get measurements for the period
        measurements = self.get_measurements(agreement_id, start_date=start_date, end_date=end_date)
        
        # Generate report
        return self.reporter.generate_sla_report(agreement, measurements, start_date, end_date)
    
    def _update_compliance_stats(self):
        """Update overall compliance statistics"""
        
        if not self.measurements:
            self.stats["average_compliance"] = 0.0
            return
        
        # Calculate compliance across all measurements
        total_measurements = len(self.measurements)
        met_measurements = sum(1 for m in self.measurements if m.target_met)
        
        self.stats["average_compliance"] = (met_measurements / total_measurements) * 100
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data for service level monitoring"""
        
        dashboard = {
            "summary": {
                "total_agreements": len(self.agreements),
                "active_agreements": sum(1 for a in self.agreements.values() if a.is_active()),
                "total_measurements": len(self.measurements),
                "recent_breaches": len([b for b in self.breaches if b.breach_date >= datetime.now() - timedelta(days=7)]),
                "average_compliance": self.stats["average_compliance"]
            },
            "agreement_status": [],
            "recent_breaches": [],
            "compliance_trends": {},
            "alerts": []
        }
        
        # Agreement status
        for agreement in self.agreements.values():
            if not agreement.is_active():
                continue
            
            recent_measurements = self.get_measurements(
                agreement.id,
                start_date=datetime.now() - timedelta(days=7)
            )
            
            if recent_measurements:
                compliance = (sum(1 for m in recent_measurements if m.target_met) / 
                            len(recent_measurements)) * 100
            else:
                compliance = 0.0
            
            dashboard["agreement_status"].append({
                "id": agreement.id,
                "name": agreement.name,
                "service": agreement.service_name,
                "customer": agreement.customer,
                "compliance": compliance,
                "target_count": len(agreement.targets),
                "measurement_count": len(recent_measurements)
            })
        
        # Recent breaches
        recent_breaches = sorted(
            [b for b in self.breaches if b.breach_date >= datetime.now() - timedelta(days=7)],
            key=lambda x: x.breach_date,
            reverse=True
        )[:10]
        
        for breach in recent_breaches:
            agreement = self.agreements.get(breach.agreement_id)
            target = agreement.get_target(breach.target_id) if agreement else None
            
            dashboard["recent_breaches"].append({
                "id": breach.id,
                "agreement_name": agreement.name if agreement else "Unknown",
                "target_name": target.name if target else "Unknown",
                "severity": breach.severity.value,
                "breach_date": breach.breach_date.isoformat(),
                "variance": breach.variance,
                "status": breach.status
            })
        
        return dashboard
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service level management statistics"""
        return {
            **self.stats,
            "agreements_by_status": {
                "active": sum(1 for a in self.agreements.values() if a.is_active()),
                "inactive": sum(1 for a in self.agreements.values() if not a.is_active())
            },
            "breaches_by_severity": {
                severity.value: sum(1 for b in self.breaches if b.severity == severity)
                for severity in AlertSeverity
            },
            "measurements_last_30_days": len([
                m for m in self.measurements 
                if m.measurement_date >= datetime.now() - timedelta(days=30)
            ])
        }


async def main():
    """Main function to demonstrate service level management"""
    print("📊 ITIL 4 Service Level Management")
    print("=" * 50)
    
    # Initialize managers
    from practices.incident_management import IncidentManager
    incident_manager = IncidentManager()
    slm_manager = ServiceLevelManager(incident_manager)
    
    print("✅ Service Level Manager initialized with sample data")
    
    # Display statistics
    stats = slm_manager.get_statistics()
    print(f"\n📈 Service Level Statistics:")
    print(f"Total Agreements: {stats['total_agreements']}")
    print(f"Active Agreements: {stats['agreements_by_status']['active']}")
    print(f"Total Measurements: {stats['total_measurements']}")
    print(f"Total Breaches: {stats['total_breaches']}")
    print(f"Average Compliance: {stats['average_compliance']:.1f}%")
    
    print(f"\nBreaches by Severity:")
    for severity, count in stats['breaches_by_severity'].items():
        if count > 0:
            print(f"  {severity}: {count}")
    
    # Display agreements
    print(f"\n📋 Service Level Agreements:")
    for agreement in slm_manager.agreements.values():
        print(f"  {agreement.name}:")
        print(f"    Service: {agreement.service_name}")
        print(f"    Customer: {agreement.customer}")
        print(f"    Status: {'Active' if agreement.is_active() else 'Inactive'}")
        print(f"    Targets: {len(agreement.targets)}")
        
        for target in agreement.targets:
            print(f"      - {target.name}: {target.target_operator} {target.target_value} {target.unit}")
    
    # Generate a sample report
    print(f"\n📊 Sample SLA Report:")
    
    # Get first agreement for demo
    first_agreement_id = next(iter(slm_manager.agreements.keys()))
    report = slm_manager.generate_report(first_agreement_id, ReportingPeriod.MONTHLY)
    
    print(f"Agreement: {report['agreement_name']}")
    print(f"Service: {report['service_name']}")
    print(f"Period: {report['reporting_period']['start'][:10]} to {report['reporting_period']['end'][:10]}")
    print(f"Overall Compliance: {report['summary']['overall_compliance']:.1f}%")
    print(f"Targets Met: {report['summary']['targets_met']}")
    print(f"Targets Breached: {report['summary']['targets_breached']}")
    
    print(f"\nTarget Performance:")
    for target_perf in report['target_performance']:
        print(f"  {target_perf['target_name']}:")
        print(f"    Target: {target_perf['target_operator']} {target_perf['target_value']} {target_perf['unit']}")
        print(f"    Average: {target_perf['average_value']:.2f} {target_perf['unit']}")
        print(f"    Compliance: {target_perf['compliance_percentage']:.1f}%")
        print(f"    Trend: {target_perf['trend']}")
        if target_perf['breach_count'] > 0:
            print(f"    Breaches: {target_perf['breach_count']}")
    
    if report['recommendations']:
        print(f"\nRecommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    # Display recent breaches
    recent_breaches = slm_manager.get_breaches()
    if recent_breaches:
        print(f"\n🚨 Recent SLA Breaches:")
        for breach in recent_breaches[-5:]:  # Show last 5 breaches
            agreement = slm_manager.get_agreement(breach.agreement_id)
            target = agreement.get_target(breach.target_id) if agreement else None
            
            print(f"  Breach {breach.id}:")
            print(f"    Agreement: {agreement.name if agreement else 'Unknown'}")
            print(f"    Target: {target.name if target else 'Unknown'}")
            print(f"    Severity: {breach.severity.value}")
            print(f"    Date: {breach.breach_date.strftime('%Y-%m-%d %H:%M')}")
            print(f"    Expected: {breach.target_value}, Actual: {breach.actual_value}")
            print(f"    Status: {breach.status}")
            if breach.incident_id:
                print(f"    Incident Created: {breach.incident_id}")
    
    # Display dashboard data
    print(f"\n📈 Service Level Dashboard:")
    dashboard = slm_manager.get_dashboard_data()
    
    print(f"Summary:")
    for key, value in dashboard['summary'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print(f"\nAgreement Status:")
    for agreement_status in dashboard['agreement_status']:
        print(f"  {agreement_status['name']}: {agreement_status['compliance']:.1f}% compliance")
    
    # Demonstrate real-time measurement recording
    print(f"\n🔄 Recording Real-time Measurements:")
    
    # Record some new measurements
    agreement_id = first_agreement_id
    agreement = slm_manager.get_agreement(agreement_id)
    
    if agreement and agreement.targets:
        target = agreement.targets[0]
        
        # Record a good measurement
        good_measurement = ServiceLevelMeasurement(
            agreement_id=agreement_id,
            target_id=target.id,
            measurement_date=datetime.now(),
            measurement_period_start=datetime.now() - timedelta(hours=1),
            measurement_period_end=datetime.now(),
            actual_value=target.target_value + 1.0,  # Better than target
            target_value=target.target_value,
            target_met=True,
            alert_severity=AlertSeverity.INFO,
            data_points=60
        )
        
        slm_manager.record_measurement(good_measurement)
        print(f"✅ Recorded good measurement: {good_measurement.actual_value} {target.unit}")
        
        # Record a breach measurement
        breach_measurement = ServiceLevelMeasurement(
            agreement_id=agreement_id,
            target_id=target.id,
            measurement_date=datetime.now(),
            measurement_period_start=datetime.now() - timedelta(hours=1),
            measurement_period_end=datetime.now(),
            actual_value=target.target_value - 5.0,  # Worse than target
            target_value=target.target_value,
            target_met=False,
            alert_severity=AlertSeverity.BREACH,
            data_points=60
        )
        
        slm_manager.record_measurement(breach_measurement)
        print(f"🚨 Recorded breach measurement: {breach_measurement.actual_value} {target.unit}")
        
        # Wait for incident creation
        await asyncio.sleep(1)
        
        # Check if incident was created
        latest_breach = slm_manager.breaches[-1] if slm_manager.breaches else None
        if latest_breach and latest_breach.incident_id:
            print(f"🎫 Incident created for breach: {latest_breach.incident_id}")
    
    print(f"\n🎉 Service Level Management Demo Complete!")
    print("Key Features Demonstrated:")
    print("✅ SLA/OLA/UC management")
    print("✅ Real-time measurement recording")
    print("✅ Automatic breach detection")
    print("✅ Incident creation for breaches")
    print("✅ Comprehensive reporting")
    print("✅ Trend analysis and recommendations")
    print("✅ Dashboard and monitoring")


if __name__ == "__main__":
    asyncio.run(main())