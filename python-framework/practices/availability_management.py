"""
ITIL 4 Availability Management Practice Implementation

This module provides comprehensive availability management capabilities including:
- Service availability monitoring and measurement
- Availability SLA tracking and reporting
- Incident impact analysis for availability
- Proactive availability planning and design
- Redundancy and resilience assessment
- Availability risk analysis and mitigation
- Mean Time Between Failures (MTBF) and Mean Time To Repair (MTTR) calculations
- Service dependency modeling for availability impact
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
import asyncio
import statistics

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.service_value_system import Priority, Status, Impact, Urgency


class AvailabilityStatus(Enum):
    """Service availability status"""
    AVAILABLE = "Available"
    UNAVAILABLE = "Unavailable"
    DEGRADED = "Degraded"
    MAINTENANCE = "Maintenance"
    UNKNOWN = "Unknown"


class OutageType(Enum):
    """Types of service outages"""
    PLANNED = "Planned"
    UNPLANNED = "Unplanned"
    PARTIAL = "Partial"
    TOTAL = "Total"


class ResilienceLevel(Enum):
    """Service resilience levels"""
    BASIC = "Basic"
    RESILIENT = "Resilient"
    HIGH_AVAILABILITY = "High Availability"
    FAULT_TOLERANT = "Fault Tolerant"
    DISASTER_TOLERANT = "Disaster Tolerant"


class AvailabilityMetricType(Enum):
    """Types of availability metrics"""
    SERVICE_AVAILABILITY = "Service Availability"
    COMPONENT_AVAILABILITY = "Component Availability"
    MTBF = "Mean Time Between Failures"
    MTTR = "Mean Time To Repair"
    MTBSI = "Mean Time Between Service Incidents"
    DOWNTIME = "Downtime"
    UPTIME = "Uptime"


@dataclass
class AvailabilityRequirement:
    """Availability requirement definition"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service_id: str = ""
    service_name: str = ""
    
    # Availability targets
    target_availability_percentage: float = 99.9
    target_mtbf_hours: float = 720.0  # 30 days
    target_mttr_hours: float = 4.0
    target_mtbsi_hours: float = 168.0  # 1 week
    
    # Business requirements
    business_hours: str = "24x7"
    critical_business_functions: List[str] = field(default_factory=list)
    maximum_tolerable_downtime: float = 4.0  # hours
    recovery_time_objective: float = 1.0  # hours
    recovery_point_objective: float = 0.5  # hours
    
    # Measurement periods
    measurement_period: str = "Monthly"
    reporting_period: str = "Monthly"
    
    # Created metadata
    created_date: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    approved_by: str = ""
    
    def calculate_allowed_downtime_per_period(self, period_hours: float = 730) -> float:
        """Calculate allowed downtime for a period based on availability target"""
        return period_hours * (1 - self.target_availability_percentage / 100)
    
    def is_availability_target_met(self, actual_availability: float) -> bool:
        """Check if availability target is met"""
        return actual_availability >= self.target_availability_percentage


@dataclass
class ServiceOutage:
    """Service outage record"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service_id: str = ""
    service_name: str = ""
    
    # Outage details
    outage_type: OutageType = OutageType.UNPLANNED
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_minutes: float = 0.0
    
    # Impact assessment
    affected_users: int = 0
    affected_business_functions: List[str] = field(default_factory=list)
    impact_level: Impact = Impact.MEDIUM
    
    # Root cause and resolution
    root_cause: str = ""
    resolution_summary: str = ""
    related_incident_id: Optional[str] = None
    related_problem_id: Optional[str] = None
    
    # Prevention measures
    preventive_actions: List[str] = field(default_factory=list)
    lessons_learned: str = ""
    
    def calculate_duration(self) -> float:
        """Calculate outage duration in minutes"""
        if not self.end_time:
            return (datetime.now() - self.start_time).total_seconds() / 60
        return (self.end_time - self.start_time).total_seconds() / 60
    
    def is_ongoing(self) -> bool:
        """Check if outage is still ongoing"""
        return self.end_time is None


@dataclass
class AvailabilityMeasurement:
    """Availability measurement record"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service_id: str = ""
    service_name: str = ""
    component_id: Optional[str] = None
    component_name: Optional[str] = None
    
    # Measurement details
    measurement_date: datetime = field(default_factory=datetime.now)
    measurement_period_start: datetime = field(default_factory=datetime.now)
    measurement_period_end: datetime = field(default_factory=datetime.now)
    
    # Availability metrics
    total_time_minutes: float = 0.0
    available_time_minutes: float = 0.0
    unavailable_time_minutes: float = 0.0
    availability_percentage: float = 0.0
    
    # Reliability metrics
    mtbf_hours: float = 0.0
    mttr_hours: float = 0.0
    mtbsi_hours: float = 0.0
    number_of_failures: int = 0
    number_of_incidents: int = 0
    
    # Outage breakdown
    planned_downtime_minutes: float = 0.0
    unplanned_downtime_minutes: float = 0.0
    
    def calculate_availability_percentage(self) -> float:
        """Calculate availability percentage"""
        if self.total_time_minutes == 0:
            return 0.0
        return (self.available_time_minutes / self.total_time_minutes) * 100


@dataclass
class ServiceDependency:
    """Service dependency for availability modeling"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_service_id: str = ""
    to_service_id: str = ""
    dependency_type: str = "Critical"  # Critical, Important, Optional
    impact_factor: float = 1.0  # 0.0 to 1.0
    recovery_dependency: bool = True
    
    def calculate_availability_contribution(self, dependent_availability: float) -> float:
        """Calculate how much this dependency contributes to overall availability"""
        if self.dependency_type == "Critical":
            return dependent_availability * self.impact_factor
        elif self.dependency_type == "Important":
            return dependent_availability * self.impact_factor * 0.7
        else:  # Optional
            return dependent_availability * self.impact_factor * 0.3


@dataclass
class ResilienceAssessment:
    """Service resilience assessment"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service_id: str = ""
    service_name: str = ""
    
    # Assessment details
    assessment_date: datetime = field(default_factory=datetime.now)
    assessor: str = ""
    
    # Current resilience level
    current_resilience_level: ResilienceLevel = ResilienceLevel.BASIC
    target_resilience_level: ResilienceLevel = ResilienceLevel.RESILIENT
    
    # Single points of failure
    single_points_of_failure: List[str] = field(default_factory=list)
    critical_dependencies: List[str] = field(default_factory=list)
    
    # Resilience features
    redundancy_implemented: bool = False
    failover_capabilities: bool = False
    backup_systems: bool = False
    disaster_recovery_plan: bool = False
    business_continuity_plan: bool = False
    
    # Risk assessment
    availability_risks: List[Dict[str, Any]] = field(default_factory=list)
    risk_mitigation_actions: List[str] = field(default_factory=list)
    
    # Improvement recommendations
    recommendations: List[str] = field(default_factory=list)
    estimated_cost: Decimal = Decimal('0.00')
    expected_availability_improvement: float = 0.0
    
    def calculate_resilience_score(self) -> float:
        """Calculate overall resilience score"""
        score = 0.0
        
        # Base score from resilience level
        level_scores = {
            ResilienceLevel.BASIC: 20.0,
            ResilienceLevel.RESILIENT: 40.0,
            ResilienceLevel.HIGH_AVAILABILITY: 60.0,
            ResilienceLevel.FAULT_TOLERANT: 80.0,
            ResilienceLevel.DISASTER_TOLERANT: 90.0
        }
        score += level_scores.get(self.current_resilience_level, 0.0)
        
        # Add points for resilience features
        if self.redundancy_implemented:
            score += 10.0
        if self.failover_capabilities:
            score += 10.0
        if self.backup_systems:
            score += 5.0
        if self.disaster_recovery_plan:
            score += 5.0
        if self.business_continuity_plan:
            score += 5.0
        
        # Subtract points for risks
        score -= len(self.single_points_of_failure) * 2.0
        score -= len(self.availability_risks) * 1.0
        
        return max(0.0, min(100.0, score))


class AvailabilityMonitor:
    """Real-time availability monitoring"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.monitored_services: Dict[str, Dict[str, Any]] = {}
        self.monitoring_active = False
        
    def add_service_monitor(self, service_id: str, service_name: str, 
                          check_interval: int = 60, check_url: Optional[str] = None):
        """Add a service to monitoring"""
        
        self.monitored_services[service_id] = {
            "service_name": service_name,
            "check_interval": check_interval,
            "check_url": check_url,
            "last_check": None,
            "status": AvailabilityStatus.UNKNOWN,
            "consecutive_failures": 0,
            "total_checks": 0,
            "successful_checks": 0
        }
        
        self.logger.info(f"Added service {service_name} to availability monitoring")
    
    async def check_service_availability(self, service_id: str) -> bool:
        """Check if a service is available"""
        
        if service_id not in self.monitored_services:
            return False
        
        service_info = self.monitored_services[service_id]
        
        # Mock availability check - in real implementation, this would:
        # - Make HTTP requests to health endpoints
        # - Check database connectivity
        # - Verify service processes
        # - Test critical functionality
        
        # Simulate occasional failures for demonstration
        import random
        is_available = random.random() > 0.05  # 95% success rate
        
        service_info["last_check"] = datetime.now()
        service_info["total_checks"] += 1
        
        if is_available:
            service_info["status"] = AvailabilityStatus.AVAILABLE
            service_info["consecutive_failures"] = 0
            service_info["successful_checks"] += 1
        else:
            service_info["status"] = AvailabilityStatus.UNAVAILABLE
            service_info["consecutive_failures"] += 1
        
        return is_available
    
    async def start_monitoring(self):
        """Start continuous availability monitoring"""
        
        self.monitoring_active = True
        self.logger.info("Started availability monitoring")
        
        while self.monitoring_active:
            for service_id in self.monitored_services:
                await self.check_service_availability(service_id)
            
            # Wait before next monitoring cycle
            await asyncio.sleep(30)  # Check every 30 seconds for demo
    
    def stop_monitoring(self):
        """Stop availability monitoring"""
        self.monitoring_active = False
        self.logger.info("Stopped availability monitoring")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        
        status = {
            "monitoring_active": self.monitoring_active,
            "monitored_services": len(self.monitored_services),
            "services": {}
        }
        
        for service_id, service_info in self.monitored_services.items():
            uptime_percentage = 0.0
            if service_info["total_checks"] > 0:
                uptime_percentage = (service_info["successful_checks"] / 
                                   service_info["total_checks"]) * 100
            
            status["services"][service_id] = {
                "name": service_info["service_name"],
                "status": service_info["status"].value,
                "last_check": service_info["last_check"].isoformat() if service_info["last_check"] else None,
                "consecutive_failures": service_info["consecutive_failures"],
                "uptime_percentage": uptime_percentage,
                "total_checks": service_info["total_checks"]
            }
        
        return status


class AvailabilityManager:
    """Main Availability Management system"""
    
    def __init__(self):
        self.requirements: Dict[str, AvailabilityRequirement] = {}
        self.outages: Dict[str, ServiceOutage] = {}
        self.measurements: Dict[str, List[AvailabilityMeasurement]] = defaultdict(list)
        self.dependencies: Dict[str, List[ServiceDependency]] = defaultdict(list)
        self.assessments: Dict[str, ResilienceAssessment] = {}
        self.monitor = AvailabilityMonitor()
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.stats = {
            "total_services": 0,
            "services_meeting_targets": 0,
            "average_availability": 0.0,
            "total_outages_this_month": 0,
            "total_downtime_minutes": 0.0,
            "mtbf_hours": 0.0,
            "mttr_hours": 0.0
        }
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample availability data"""
        
        # Sample availability requirements
        web_service_req = AvailabilityRequirement(
            service_id="SVC-001",
            service_name="Customer Web Portal",
            target_availability_percentage=99.9,
            target_mtbf_hours=720.0,
            target_mttr_hours=2.0,
            business_hours="24x7",
            critical_business_functions=["Customer Login", "Order Processing", "Payment"],
            maximum_tolerable_downtime=1.0,
            recovery_time_objective=0.5,
            created_by="Availability Manager"
        )
        
        database_req = AvailabilityRequirement(
            service_id="SVC-002",
            service_name="Customer Database",
            target_availability_percentage=99.95,
            target_mtbf_hours=1440.0,
            target_mttr_hours=1.0,
            business_hours="24x7",
            critical_business_functions=["Data Storage", "Data Retrieval", "Backup"],
            maximum_tolerable_downtime=0.5,
            recovery_time_objective=0.25,
            created_by="Database Administrator"
        )
        
        email_service_req = AvailabilityRequirement(
            service_id="SVC-003",
            service_name="Email Service",
            target_availability_percentage=99.5,
            target_mtbf_hours=168.0,
            target_mttr_hours=4.0,
            business_hours="8x5",
            critical_business_functions=["Email Delivery", "Email Storage"],
            maximum_tolerable_downtime=8.0,
            recovery_time_objective=2.0,
            created_by="IT Operations"
        )
        
        self.add_availability_requirement(web_service_req)
        self.add_availability_requirement(database_req)
        self.add_availability_requirement(email_service_req)
        
        # Sample service dependencies
        web_to_db_dep = ServiceDependency(
            from_service_id="SVC-001",
            to_service_id="SVC-002",
            dependency_type="Critical",
            impact_factor=1.0
        )
        
        web_to_email_dep = ServiceDependency(
            from_service_id="SVC-001",
            to_service_id="SVC-003",
            dependency_type="Important",
            impact_factor=0.3
        )
        
        self.add_service_dependency(web_to_db_dep)
        self.add_service_dependency(web_to_email_dep)
        
        # Sample outages
        past_outage = ServiceOutage(
            service_id="SVC-001",
            service_name="Customer Web Portal",
            outage_type=OutageType.UNPLANNED,
            start_time=datetime.now() - timedelta(days=15, hours=2),
            end_time=datetime.now() - timedelta(days=15, hours=0, minutes=30),
            affected_users=500,
            affected_business_functions=["Customer Login", "Order Processing"],
            impact_level=Impact.HIGH,
            root_cause="Database connection timeout",
            resolution_summary="Restarted database connection pool",
            related_incident_id="INC-001234"
        )
        past_outage.duration_minutes = past_outage.calculate_duration()
        
        planned_outage = ServiceOutage(
            service_id="SVC-002",
            service_name="Customer Database",
            outage_type=OutageType.PLANNED,
            start_time=datetime.now() - timedelta(days=7, hours=2),
            end_time=datetime.now() - timedelta(days=7, hours=1),
            affected_users=1000,
            affected_business_functions=["All Database Operations"],
            impact_level=Impact.MEDIUM,
            root_cause="Scheduled maintenance",
            resolution_summary="Database patching completed successfully"
        )
        planned_outage.duration_minutes = planned_outage.calculate_duration()
        
        self.record_outage(past_outage)
        self.record_outage(planned_outage)
        
        # Sample availability measurements
        self._generate_sample_measurements()
        
        # Sample resilience assessments
        web_assessment = ResilienceAssessment(
            service_id="SVC-001",
            service_name="Customer Web Portal",
            assessor="Availability Manager",
            current_resilience_level=ResilienceLevel.RESILIENT,
            target_resilience_level=ResilienceLevel.HIGH_AVAILABILITY,
            single_points_of_failure=["Load Balancer", "Database Connection"],
            redundancy_implemented=True,
            failover_capabilities=True,
            backup_systems=True,
            disaster_recovery_plan=True,
            availability_risks=[
                {"risk": "Database failure", "probability": "Medium", "impact": "High"},
                {"risk": "Network outage", "probability": "Low", "impact": "High"}
            ],
            recommendations=[
                "Implement database clustering",
                "Add redundant network connections",
                "Set up secondary data center"
            ],
            estimated_cost=Decimal('75000.00'),
            expected_availability_improvement=0.05
        )
        
        self.conduct_resilience_assessment(web_assessment)
        
        # Add services to monitoring
        self.monitor.add_service_monitor("SVC-001", "Customer Web Portal", 60, "https://portal.example.com/health")
        self.monitor.add_service_monitor("SVC-002", "Customer Database", 30, "tcp://db.example.com:5432")
        self.monitor.add_service_monitor("SVC-003", "Email Service", 120, "smtp://mail.example.com:587")
    
    def _generate_sample_measurements(self):
        """Generate sample availability measurements"""
        
        # Generate monthly measurements for the last 6 months
        for months_ago in range(6, 0, -1):
            measurement_date = datetime.now() - timedelta(days=months_ago * 30)
            period_start = measurement_date.replace(day=1)
            period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            
            # Web service measurement
            web_measurement = AvailabilityMeasurement(
                service_id="SVC-001",
                service_name="Customer Web Portal",
                measurement_date=measurement_date,
                measurement_period_start=period_start,
                measurement_period_end=period_end,
                total_time_minutes=30 * 24 * 60,  # 30 days
                available_time_minutes=30 * 24 * 60 - 90,  # 90 minutes downtime
                unavailable_time_minutes=90,
                availability_percentage=99.79,
                mtbf_hours=720,
                mttr_hours=1.5,
                mtbsi_hours=720,
                number_of_failures=1,
                number_of_incidents=1,
                planned_downtime_minutes=30,
                unplanned_downtime_minutes=60
            )
            
            # Database measurement
            db_measurement = AvailabilityMeasurement(
                service_id="SVC-002",
                service_name="Customer Database",
                measurement_date=measurement_date,
                measurement_period_start=period_start,
                measurement_period_end=period_end,
                total_time_minutes=30 * 24 * 60,
                available_time_minutes=30 * 24 * 60 - 60,  # 60 minutes downtime
                unavailable_time_minutes=60,
                availability_percentage=99.86,
                mtbf_hours=1440,
                mttr_hours=1.0,
                mtbsi_hours=1440,
                number_of_failures=1,
                number_of_incidents=1,
                planned_downtime_minutes=60,
                unplanned_downtime_minutes=0
            )
            
            self.record_measurement(web_measurement)
            self.record_measurement(db_measurement)
    
    def add_availability_requirement(self, requirement: AvailabilityRequirement) -> str:
        """Add availability requirement for a service"""
        
        self.requirements[requirement.service_id] = requirement
        self._update_statistics()
        
        self.logger.info(f"Added availability requirement for {requirement.service_name}")
        return requirement.id
    
    def get_availability_requirement(self, service_id: str) -> Optional[AvailabilityRequirement]:
        """Get availability requirement for a service"""
        return self.requirements.get(service_id)
    
    def record_outage(self, outage: ServiceOutage) -> str:
        """Record a service outage"""
        
        self.outages[outage.id] = outage
        self._update_statistics()
        
        self.logger.info(f"Recorded outage for {outage.service_name}: {outage.duration_minutes} minutes")
        return outage.id
    
    def end_outage(self, outage_id: str, resolution_summary: str = "") -> bool:
        """End an ongoing outage"""
        
        outage = self.outages.get(outage_id)
        if not outage or outage.end_time:
            return False
        
        outage.end_time = datetime.now()
        outage.duration_minutes = outage.calculate_duration()
        outage.resolution_summary = resolution_summary
        
        self._update_statistics()
        
        self.logger.info(f"Ended outage {outage_id}: total duration {outage.duration_minutes} minutes")
        return True
    
    def record_measurement(self, measurement: AvailabilityMeasurement) -> str:
        """Record an availability measurement"""
        
        self.measurements[measurement.service_id].append(measurement)
        self._update_statistics()
        
        self.logger.info(f"Recorded availability measurement for {measurement.service_name}: {measurement.availability_percentage}%")
        return measurement.id
    
    def add_service_dependency(self, dependency: ServiceDependency) -> str:
        """Add a service dependency"""
        
        self.dependencies[dependency.from_service_id].append(dependency)
        
        self.logger.info(f"Added dependency: {dependency.from_service_id} -> {dependency.to_service_id}")
        return dependency.id
    
    def conduct_resilience_assessment(self, assessment: ResilienceAssessment) -> str:
        """Conduct a service resilience assessment"""
        
        self.assessments[assessment.service_id] = assessment
        
        self.logger.info(f"Conducted resilience assessment for {assessment.service_name}")
        return assessment.id
    
    def calculate_service_availability(self, service_id: str, 
                                     period_days: int = 30) -> Dict[str, Any]:
        """Calculate current availability for a service"""
        
        cutoff_date = datetime.now() - timedelta(days=period_days)
        
        # Get recent measurements
        recent_measurements = [
            m for m in self.measurements.get(service_id, [])
            if m.measurement_date >= cutoff_date
        ]
        
        if not recent_measurements:
            return {"error": "No measurements available"}
        
        # Calculate aggregated metrics
        total_time = sum(m.total_time_minutes for m in recent_measurements)
        available_time = sum(m.available_time_minutes for m in recent_measurements)
        unavailable_time = sum(m.unavailable_time_minutes for m in recent_measurements)
        
        availability_percentage = (available_time / total_time) * 100 if total_time > 0 else 0
        
        # Calculate MTBF and MTTR
        total_failures = sum(m.number_of_failures for m in recent_measurements)
        total_incidents = sum(m.number_of_incidents for m in recent_measurements)
        
        mtbf_hours = (available_time / 60) / max(total_failures, 1)
        mttr_hours = (unavailable_time / 60) / max(total_failures, 1)
        
        return {
            "service_id": service_id,
            "period_days": period_days,
            "availability_percentage": availability_percentage,
            "total_time_minutes": total_time,
            "available_time_minutes": available_time,
            "unavailable_time_minutes": unavailable_time,
            "mtbf_hours": mtbf_hours,
            "mttr_hours": mttr_hours,
            "number_of_failures": total_failures,
            "number_of_incidents": total_incidents
        }
    
    def calculate_composite_availability(self, service_id: str) -> Dict[str, Any]:
        """Calculate composite availability including dependencies"""
        
        # Get direct service availability
        service_availability = self.calculate_service_availability(service_id)
        
        if "error" in service_availability:
            return service_availability
        
        # Get service dependencies
        dependencies = self.dependencies.get(service_id, [])
        
        composite_calc = {
            "service_id": service_id,
            "direct_availability": service_availability["availability_percentage"],
            "dependencies": [],
            "composite_availability": service_availability["availability_percentage"]
        }
        
        # Calculate impact of each dependency
        total_dependency_impact = 0.0
        
        for dependency in dependencies:
            dep_availability = self.calculate_service_availability(dependency.to_service_id)
            
            if "error" not in dep_availability:
                impact = dependency.calculate_availability_contribution(
                    dep_availability["availability_percentage"]
                )
                
                composite_calc["dependencies"].append({
                    "service_id": dependency.to_service_id,
                    "dependency_type": dependency.dependency_type,
                    "availability": dep_availability["availability_percentage"],
                    "impact_factor": dependency.impact_factor,
                    "contribution": impact
                })
                
                total_dependency_impact += (100 - impact) * (dependency.impact_factor / 100)
        
        # Adjust composite availability based on dependencies
        if dependencies:
            composite_calc["composite_availability"] = max(
                0.0, 
                service_availability["availability_percentage"] - total_dependency_impact
            )
        
        return composite_calc
    
    def analyze_availability_trends(self, service_id: str, 
                                   months: int = 6) -> Dict[str, Any]:
        """Analyze availability trends over time"""
        
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        
        measurements = [
            m for m in self.measurements.get(service_id, [])
            if m.measurement_date >= cutoff_date
        ]
        
        if not measurements:
            return {"error": "No measurements available"}
        
        # Sort by date
        measurements.sort(key=lambda x: x.measurement_date)
        
        # Calculate trend data
        trend_data = []
        availability_values = []
        mtbf_values = []
        mttr_values = []
        
        for measurement in measurements:
            trend_data.append({
                "date": measurement.measurement_date.isoformat(),
                "availability": measurement.availability_percentage,
                "mtbf_hours": measurement.mtbf_hours,
                "mttr_hours": measurement.mttr_hours,
                "downtime_minutes": measurement.unavailable_time_minutes
            })
            
            availability_values.append(measurement.availability_percentage)
            mtbf_values.append(measurement.mtbf_hours)
            mttr_values.append(measurement.mttr_hours)
        
        # Calculate statistics
        analysis = {
            "service_id": service_id,
            "analysis_period_months": months,
            "measurements_count": len(measurements),
            "trend_data": trend_data,
            "statistics": {
                "average_availability": statistics.mean(availability_values) if availability_values else 0,
                "min_availability": min(availability_values) if availability_values else 0,
                "max_availability": max(availability_values) if availability_values else 0,
                "availability_std_dev": statistics.stdev(availability_values) if len(availability_values) > 1 else 0,
                "average_mtbf": statistics.mean(mtbf_values) if mtbf_values else 0,
                "average_mttr": statistics.mean(mttr_values) if mttr_values else 0
            }
        }
        
        # Determine trend direction
        if len(availability_values) >= 2:
            recent_avg = statistics.mean(availability_values[-3:]) if len(availability_values) >= 3 else availability_values[-1]
            older_avg = statistics.mean(availability_values[:3]) if len(availability_values) >= 3 else availability_values[0]
            
            if recent_avg > older_avg + 0.1:
                analysis["trend_direction"] = "Improving"
            elif recent_avg < older_avg - 0.1:
                analysis["trend_direction"] = "Declining"
            else:
                analysis["trend_direction"] = "Stable"
        else:
            analysis["trend_direction"] = "Insufficient Data"
        
        return analysis
    
    def get_availability_dashboard(self) -> Dict[str, Any]:
        """Get availability management dashboard data"""
        
        dashboard = {
            "generated_date": datetime.now().isoformat(),
            "summary": self.get_statistics(),
            "service_status": {},
            "recent_outages": [],
            "availability_targets": {},
            "monitoring_status": self.monitor.get_monitoring_status()
        }
        
        # Service status summary
        for service_id, requirement in self.requirements.items():
            availability = self.calculate_service_availability(service_id)
            
            if "error" not in availability:
                target_met = requirement.is_availability_target_met(availability["availability_percentage"])
                
                dashboard["service_status"][service_id] = {
                    "service_name": requirement.service_name,
                    "current_availability": availability["availability_percentage"],
                    "target_availability": requirement.target_availability_percentage,
                    "target_met": target_met,
                    "mtbf_hours": availability["mtbf_hours"],
                    "mttr_hours": availability["mttr_hours"]
                }
                
                dashboard["availability_targets"][service_id] = {
                    "service_name": requirement.service_name,
                    "target": requirement.target_availability_percentage,
                    "actual": availability["availability_percentage"],
                    "status": "Met" if target_met else "Not Met"
                }
        
        # Recent outages (last 30 days)
        recent_cutoff = datetime.now() - timedelta(days=30)
        recent_outages = [
            outage for outage in self.outages.values()
            if outage.start_time >= recent_cutoff
        ]
        
        recent_outages.sort(key=lambda x: x.start_time, reverse=True)
        
        for outage in recent_outages[:10]:  # Top 10 recent outages
            dashboard["recent_outages"].append({
                "service_name": outage.service_name,
                "outage_type": outage.outage_type.value,
                "start_time": outage.start_time.isoformat(),
                "end_time": outage.end_time.isoformat() if outage.end_time else None,
                "duration_minutes": outage.duration_minutes,
                "impact_level": outage.impact_level.value,
                "affected_users": outage.affected_users,
                "is_ongoing": outage.is_ongoing()
            })
        
        return dashboard
    
    def generate_availability_report(self, report_type: str = "summary", 
                                   service_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive availability report"""
        
        if report_type == "summary":
            return self._generate_summary_report()
        elif report_type == "detailed" and service_id:
            return self._generate_detailed_service_report(service_id)
        elif report_type == "sla_compliance":
            return self._generate_sla_compliance_report()
        elif report_type == "resilience":
            return self._generate_resilience_report()
        else:
            return {"error": "Invalid report type or missing service_id"}
    
    def _generate_summary_report(self) -> Dict[str, Any]:
        """Generate summary availability report"""
        
        return {
            "report_type": "Availability Summary",
            "generated_date": datetime.now().isoformat(),
            "statistics": self.get_statistics(),
            "service_performance": {
                service_id: {
                    "service_name": req.service_name,
                    "target": req.target_availability_percentage,
                    "actual": self.calculate_service_availability(service_id).get("availability_percentage", 0),
                    "status": "Met" if self.calculate_service_availability(service_id).get("availability_percentage", 0) >= req.target_availability_percentage else "Not Met"
                }
                for service_id, req in self.requirements.items()
            },
            "outage_summary": {
                "total_outages": len(self.outages),
                "planned_outages": len([o for o in self.outages.values() if o.outage_type == OutageType.PLANNED]),
                "unplanned_outages": len([o for o in self.outages.values() if o.outage_type == OutageType.UNPLANNED]),
                "total_downtime_minutes": sum(o.duration_minutes for o in self.outages.values())
            }
        }
    
    def _generate_detailed_service_report(self, service_id: str) -> Dict[str, Any]:
        """Generate detailed service availability report"""
        
        requirement = self.requirements.get(service_id)
        if not requirement:
            return {"error": "Service not found"}
        
        availability = self.calculate_service_availability(service_id)
        composite = self.calculate_composite_availability(service_id)
        trends = self.analyze_availability_trends(service_id)
        
        service_outages = [o for o in self.outages.values() if o.service_id == service_id]
        assessment = self.assessments.get(service_id)
        
        return {
            "report_type": "Detailed Service Report",
            "generated_date": datetime.now().isoformat(),
            "service_info": {
                "service_id": service_id,
                "service_name": requirement.service_name,
                "business_hours": requirement.business_hours,
                "critical_functions": requirement.critical_business_functions
            },
            "requirements": {
                "target_availability": requirement.target_availability_percentage,
                "target_mtbf": requirement.target_mtbf_hours,
                "target_mttr": requirement.target_mttr_hours,
                "max_tolerable_downtime": requirement.maximum_tolerable_downtime,
                "rto": requirement.recovery_time_objective,
                "rpo": requirement.recovery_point_objective
            },
            "current_performance": availability,
            "composite_availability": composite,
            "trend_analysis": trends,
            "outage_history": [
                {
                    "outage_type": o.outage_type.value,
                    "start_time": o.start_time.isoformat(),
                    "duration_minutes": o.duration_minutes,
                    "impact_level": o.impact_level.value,
                    "affected_users": o.affected_users,
                    "root_cause": o.root_cause
                }
                for o in service_outages
            ],
            "resilience_assessment": {
                "current_level": assessment.current_resilience_level.value if assessment else "Not Assessed",
                "resilience_score": assessment.calculate_resilience_score() if assessment else 0,
                "single_points_of_failure": assessment.single_points_of_failure if assessment else [],
                "recommendations": assessment.recommendations if assessment else []
            }
        }
    
    def _generate_sla_compliance_report(self) -> Dict[str, Any]:
        """Generate SLA compliance report"""
        
        compliance_data = {}
        
        for service_id, requirement in self.requirements.items():
            availability = self.calculate_service_availability(service_id)
            
            if "error" not in availability:
                compliance_data[service_id] = {
                    "service_name": requirement.service_name,
                    "target_availability": requirement.target_availability_percentage,
                    "actual_availability": availability["availability_percentage"],
                    "compliance_status": "Compliant" if availability["availability_percentage"] >= requirement.target_availability_percentage else "Non-Compliant",
                    "target_mtbf": requirement.target_mtbf_hours,
                    "actual_mtbf": availability["mtbf_hours"],
                    "target_mttr": requirement.target_mttr_hours,
                    "actual_mttr": availability["mttr_hours"],
                    "allowed_downtime_monthly": requirement.calculate_allowed_downtime_per_period(),
                    "actual_downtime_monthly": availability["unavailable_time_minutes"]
                }
        
        return {
            "report_type": "SLA Compliance Report",
            "generated_date": datetime.now().isoformat(),
            "compliance_summary": {
                "total_services": len(compliance_data),
                "compliant_services": len([s for s in compliance_data.values() if s["compliance_status"] == "Compliant"]),
                "non_compliant_services": len([s for s in compliance_data.values() if s["compliance_status"] == "Non-Compliant"])
            },
            "service_compliance": compliance_data
        }
    
    def _generate_resilience_report(self) -> Dict[str, Any]:
        """Generate resilience assessment report"""
        
        return {
            "report_type": "Service Resilience Report",
            "generated_date": datetime.now().isoformat(),
            "assessments": {
                service_id: {
                    "service_name": assessment.service_name,
                    "current_resilience_level": assessment.current_resilience_level.value,
                    "target_resilience_level": assessment.target_resilience_level.value,
                    "resilience_score": assessment.calculate_resilience_score(),
                    "single_points_of_failure": len(assessment.single_points_of_failure),
                    "redundancy_implemented": assessment.redundancy_implemented,
                    "disaster_recovery_ready": assessment.disaster_recovery_plan,
                    "improvement_cost": str(assessment.estimated_cost),
                    "expected_improvement": assessment.expected_availability_improvement
                }
                for service_id, assessment in self.assessments.items()
            },
            "overall_resilience": {
                "average_score": statistics.mean([a.calculate_resilience_score() for a in self.assessments.values()]) if self.assessments else 0,
                "services_with_high_availability": len([a for a in self.assessments.values() if a.current_resilience_level in [ResilienceLevel.HIGH_AVAILABILITY, ResilienceLevel.FAULT_TOLERANT, ResilienceLevel.DISASTER_TOLERANT]]),
                "total_improvement_cost": str(sum([a.estimated_cost for a in self.assessments.values()]))
            }
        }
    
    def _update_statistics(self):
        """Update availability management statistics"""
        
        self.stats = {
            "total_services": len(self.requirements),
            "services_meeting_targets": 0,
            "average_availability": 0.0,
            "total_outages_this_month": 0,
            "total_downtime_minutes": 0.0,
            "mtbf_hours": 0.0,
            "mttr_hours": 0.0
        }
        
        # Calculate service performance
        availability_values = []
        mtbf_values = []
        mttr_values = []
        
        for service_id, requirement in self.requirements.items():
            availability = self.calculate_service_availability(service_id)
            
            if "error" not in availability:
                availability_values.append(availability["availability_percentage"])
                mtbf_values.append(availability["mtbf_hours"])
                mttr_values.append(availability["mttr_hours"])
                
                if availability["availability_percentage"] >= requirement.target_availability_percentage:
                    self.stats["services_meeting_targets"] += 1
        
        if availability_values:
            self.stats["average_availability"] = statistics.mean(availability_values)
        if mtbf_values:
            self.stats["mtbf_hours"] = statistics.mean(mtbf_values)
        if mttr_values:
            self.stats["mttr_hours"] = statistics.mean(mttr_values)
        
        # Calculate recent outages
        recent_cutoff = datetime.now() - timedelta(days=30)
        recent_outages = [o for o in self.outages.values() if o.start_time >= recent_cutoff]
        
        self.stats["total_outages_this_month"] = len(recent_outages)
        self.stats["total_downtime_minutes"] = sum(o.duration_minutes for o in recent_outages)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current availability management statistics"""
        return self.stats
    
    async def start_monitoring(self):
        """Start availability monitoring"""
        await self.monitor.start_monitoring()
    
    def stop_monitoring(self):
        """Stop availability monitoring"""
        self.monitor.stop_monitoring()


async def main():
    """Main function to demonstrate availability management"""
    print("🟢 ITIL 4 Availability Management")
    print("=" * 50)
    
    # Initialize availability manager
    availability_mgr = AvailabilityManager()
    
    print("✅ Availability Manager initialized with sample data")
    
    # Display statistics
    stats = availability_mgr.get_statistics()
    print(f"\n📊 Availability Management Statistics:")
    print(f"Total Services: {stats['total_services']}")
    print(f"Services Meeting Targets: {stats['services_meeting_targets']}")
    print(f"Average Availability: {stats['average_availability']:.2f}%")
    print(f"Total Outages This Month: {stats['total_outages_this_month']}")
    print(f"Total Downtime: {stats['total_downtime_minutes']:.1f} minutes")
    print(f"Average MTBF: {stats['mtbf_hours']:.1f} hours")
    print(f"Average MTTR: {stats['mttr_hours']:.1f} hours")
    
    # Show availability requirements
    print(f"\n📋 Availability Requirements:")
    for service_id, req in availability_mgr.requirements.items():
        print(f"  {req.service_name}:")
        print(f"    Target Availability: {req.target_availability_percentage}%")
        print(f"    Target MTBF: {req.target_mtbf_hours} hours")
        print(f"    Target MTTR: {req.target_mttr_hours} hours")
        print(f"    Max Tolerable Downtime: {req.maximum_tolerable_downtime} hours")
        print(f"    Business Hours: {req.business_hours}")
    
    # Service availability analysis
    print(f"\n🎯 Current Service Performance:")
    for service_id, req in availability_mgr.requirements.items():
        availability = availability_mgr.calculate_service_availability(service_id)
        
        if "error" not in availability:
            target_met = "✅" if availability["availability_percentage"] >= req.target_availability_percentage else "❌"
            print(f"  {req.service_name}: {availability['availability_percentage']:.2f}% {target_met}")
            print(f"    MTBF: {availability['mtbf_hours']:.1f}h (Target: {req.target_mtbf_hours}h)")
            print(f"    MTTR: {availability['mttr_hours']:.1f}h (Target: {req.target_mttr_hours}h)")
            print(f"    Downtime: {availability['unavailable_time_minutes']:.0f} minutes")
    
    # Composite availability (including dependencies)
    print(f"\n🔗 Composite Availability Analysis:")
    for service_id in ["SVC-001"]:  # Focus on web service which has dependencies
        composite = availability_mgr.calculate_composite_availability(service_id)
        
        if "error" not in composite:
            print(f"  {availability_mgr.requirements[service_id].service_name}:")
            print(f"    Direct Availability: {composite['direct_availability']:.2f}%")
            print(f"    Composite Availability: {composite['composite_availability']:.2f}%")
            
            if composite["dependencies"]:
                print(f"    Dependencies:")
                for dep in composite["dependencies"]:
                    print(f"      {dep['dependency_type']} dependency: {dep['availability']:.2f}%")
    
    # Availability trends
    print(f"\n📈 Availability Trends (6 months):")
    for service_id in list(availability_mgr.requirements.keys())[:2]:  # First 2 services
        trends = availability_mgr.analyze_availability_trends(service_id)
        
        if "error" not in trends:
            service_name = availability_mgr.requirements[service_id].service_name
            print(f"  {service_name}:")
            print(f"    Trend Direction: {trends['trend_direction']}")
            print(f"    Average Availability: {trends['statistics']['average_availability']:.2f}%")
            print(f"    Best Month: {trends['statistics']['max_availability']:.2f}%")
            print(f"    Worst Month: {trends['statistics']['min_availability']:.2f}%")
            print(f"    Measurements: {trends['measurements_count']}")
    
    # Recent outages analysis
    print(f"\n🚨 Recent Outages:")
    recent_cutoff = datetime.now() - timedelta(days=30)
    recent_outages = [o for o in availability_mgr.outages.values() if o.start_time >= recent_cutoff]
    
    if recent_outages:
        recent_outages.sort(key=lambda x: x.start_time, reverse=True)
        
        for outage in recent_outages[:5]:  # Show top 5
            print(f"  {outage.service_name}:")
            print(f"    Type: {outage.outage_type.value}")
            print(f"    Duration: {outage.duration_minutes:.0f} minutes")
            print(f"    Impact: {outage.impact_level.value}")
            print(f"    Affected Users: {outage.affected_users:,}")
            print(f"    Root Cause: {outage.root_cause}")
    else:
        print("  No outages in the last 30 days ✅")
    
    # Resilience assessments
    print(f"\n🛡️ Service Resilience Assessment:")
    for service_id, assessment in availability_mgr.assessments.items():
        resilience_score = assessment.calculate_resilience_score()
        print(f"  {assessment.service_name}:")
        print(f"    Current Level: {assessment.current_resilience_level.value}")
        print(f"    Target Level: {assessment.target_resilience_level.value}")
        print(f"    Resilience Score: {resilience_score:.1f}/100")
        print(f"    Single Points of Failure: {len(assessment.single_points_of_failure)}")
        print(f"    Redundancy: {'✅' if assessment.redundancy_implemented else '❌'}")
        print(f"    Disaster Recovery: {'✅' if assessment.disaster_recovery_plan else '❌'}")
        
        if assessment.recommendations:
            print(f"    Top Recommendations:")
            for rec in assessment.recommendations[:2]:
                print(f"      • {rec}")
    
    # SLA compliance report
    print(f"\n📊 SLA Compliance Report:")
    sla_report = availability_mgr.generate_availability_report("sla_compliance")
    
    compliance_summary = sla_report["compliance_summary"]
    print(f"Total Services: {compliance_summary['total_services']}")
    print(f"Compliant Services: {compliance_summary['compliant_services']} ✅")
    print(f"Non-Compliant Services: {compliance_summary['non_compliant_services']} ❌")
    
    print(f"\nCompliance Details:")
    for service_id, compliance in sla_report["service_compliance"].items():
        status_icon = "✅" if compliance["compliance_status"] == "Compliant" else "❌"
        print(f"  {compliance['service_name']}: {compliance['compliance_status']} {status_icon}")
        print(f"    Target: {compliance['target_availability']}% | Actual: {compliance['actual_availability']:.2f}%")
        
        if compliance["compliance_status"] == "Non-Compliant":
            gap = compliance["target_availability"] - compliance["actual_availability"]
            print(f"    Gap: {gap:.2f}% below target")
    
    # Monitoring status
    print(f"\n🔍 Real-time Monitoring Status:")
    monitoring_status = availability_mgr.monitor.get_monitoring_status()
    
    print(f"Monitoring Active: {'✅' if monitoring_status['monitoring_active'] else '❌'}")
    print(f"Monitored Services: {monitoring_status['monitored_services']}")
    
    for service_id, service_info in monitoring_status["services"].items():
        status_icon = {"Available": "🟢", "Unavailable": "🔴", "Degraded": "🟡", "Unknown": "⚪"}.get(service_info["status"], "⚪")
        print(f"  {service_info['name']}: {service_info['status']} {status_icon}")
        print(f"    Uptime: {service_info['uptime_percentage']:.1f}%")
        print(f"    Total Checks: {service_info['total_checks']}")
        print(f"    Consecutive Failures: {service_info['consecutive_failures']}")
    
    # Dashboard summary
    print(f"\n📈 Availability Dashboard Summary:")
    dashboard = availability_mgr.get_availability_dashboard()
    
    print(f"Services Meeting Targets: {len([s for s in dashboard['availability_targets'].values() if s['status'] == 'Met'])}/{len(dashboard['availability_targets'])}")
    print(f"Recent Outages: {len(dashboard['recent_outages'])}")
    print(f"Overall Health: {'🟢 Good' if stats['services_meeting_targets'] == stats['total_services'] else '🟡 Needs Attention'}")
    
    # Improvement recommendations
    print(f"\n🎯 Key Improvement Recommendations:")
    
    non_compliant_services = [
        s for s in sla_report["service_compliance"].values() 
        if s["compliance_status"] == "Non-Compliant"
    ]
    
    if non_compliant_services:
        print("Priority Actions:")
        for service in non_compliant_services:
            print(f"  • Improve {service['service_name']} availability by {service['target_availability'] - service['actual_availability']:.2f}%")
    
    # Show resilience improvement opportunities
    for service_id, assessment in availability_mgr.assessments.items():
        if assessment.recommendations and assessment.calculate_resilience_score() < 80:
            print(f"  • {assessment.service_name}: {assessment.recommendations[0]}")
    
    print(f"\n🎉 Availability Management Demo Complete!")
    print("Key Features Demonstrated:")
    print("✅ Availability requirements and SLA tracking")
    print("✅ Real-time service availability monitoring")
    print("✅ Outage recording and impact analysis")
    print("✅ MTBF/MTTR calculations and trending")
    print("✅ Composite availability with dependencies")
    print("✅ Service resilience assessment")
    print("✅ SLA compliance reporting")
    print("✅ Proactive availability planning")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())