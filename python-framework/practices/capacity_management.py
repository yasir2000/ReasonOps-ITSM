"""
ITIL 4 Capacity Management Practice Implementation

This module provides comprehensive capacity management capabilities including:
- Performance monitoring and capacity planning
- Resource utilization tracking and optimization
- Threshold management and alerting
- Demand forecasting and capacity modeling
- Performance bottleneck analysis
- Capacity reporting and trending
- Business and service capacity management
- Resource allocation and scaling recommendations
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
import statistics
import asyncio
import math

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.service_value_system import Priority, Status, Impact, Urgency


class ResourceType(Enum):
    """Types of IT resources"""
    CPU = "CPU"
    MEMORY = "Memory"
    STORAGE = "Storage"
    NETWORK = "Network"
    DATABASE = "Database"
    APPLICATION = "Application"
    INFRASTRUCTURE = "Infrastructure"
    CLOUD = "Cloud"
    BANDWIDTH = "Bandwidth"
    TRANSACTION = "Transaction"


class CapacityMetricType(Enum):
    """Types of capacity metrics"""
    UTILIZATION = "Utilization"
    THROUGHPUT = "Throughput"
    RESPONSE_TIME = "Response Time"
    QUEUE_LENGTH = "Queue Length"
    ERROR_RATE = "Error Rate"
    AVAILABILITY = "Availability"
    CONCURRENT_USERS = "Concurrent Users"
    TRANSACTIONS_PER_SECOND = "Transactions Per Second"


class ThresholdType(Enum):
    """Threshold alert types"""
    WARNING = "Warning"
    CRITICAL = "Critical"
    BREACH = "Breach"
    FORECAST = "Forecast"


class CapacityPlanType(Enum):
    """Types of capacity plans"""
    REACTIVE = "Reactive"
    PROACTIVE = "Proactive"
    PREDICTIVE = "Predictive"
    STRATEGIC = "Strategic"


class ScalingStrategy(Enum):
    """Resource scaling strategies"""
    VERTICAL = "Vertical"  # Scale up/down
    HORIZONTAL = "Horizontal"  # Scale out/in
    HYBRID = "Hybrid"  # Both vertical and horizontal
    ELASTIC = "Elastic"  # Auto-scaling


@dataclass
class CapacityThreshold:
    """Capacity threshold definition"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    resource_id: str = ""
    resource_name: str = ""
    metric_type: CapacityMetricType = CapacityMetricType.UTILIZATION
    
    # Threshold values (percentages or absolute values)
    warning_threshold: float = 70.0
    critical_threshold: float = 85.0
    breach_threshold: float = 95.0
    
    # Threshold settings
    threshold_type: str = "Percentage"  # Percentage or Absolute
    measurement_period_minutes: int = 15
    consecutive_breaches_required: int = 3
    
    # Actions
    warning_actions: List[str] = field(default_factory=list)
    critical_actions: List[str] = field(default_factory=list)
    breach_actions: List[str] = field(default_factory=list)
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    active: bool = True
    
    def evaluate_threshold(self, current_value: float) -> Optional[ThresholdType]:
        """Evaluate if current value breaches any threshold"""
        
        if not self.active:
            return None
        
        if current_value >= self.breach_threshold:
            return ThresholdType.BREACH
        elif current_value >= self.critical_threshold:
            return ThresholdType.CRITICAL
        elif current_value >= self.warning_threshold:
            return ThresholdType.WARNING
        
        return None
    
    def get_threshold_status(self, current_value: float) -> str:
        """Get human-readable threshold status"""
        
        threshold = self.evaluate_threshold(current_value)
        
        if threshold == ThresholdType.BREACH:
            return f"BREACH: {current_value:.1f}% >= {self.breach_threshold}%"
        elif threshold == ThresholdType.CRITICAL:
            return f"CRITICAL: {current_value:.1f}% >= {self.critical_threshold}%"
        elif threshold == ThresholdType.WARNING:
            return f"WARNING: {current_value:.1f}% >= {self.warning_threshold}%"
        else:
            return f"OK: {current_value:.1f}% within normal range"


@dataclass
class PerformanceMetric:
    """Performance measurement data point"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    resource_id: str = ""
    resource_name: str = ""
    metric_type: CapacityMetricType = CapacityMetricType.UTILIZATION
    
    # Measurement details
    timestamp: datetime = field(default_factory=datetime.now)
    value: float = 0.0
    unit: str = ""
    
    # Context
    measurement_source: str = ""  # Monitoring tool, agent, etc.
    measurement_interval_seconds: int = 300  # 5 minutes default
    
    # Additional metrics for context
    concurrent_users: Optional[int] = None
    transaction_count: Optional[int] = None
    error_count: Optional[int] = None
    
    def get_value_with_unit(self) -> str:
        """Get formatted value with unit"""
        if self.unit:
            return f"{self.value:.2f} {self.unit}"
        return f"{self.value:.2f}"


@dataclass
class CapacityForecast:
    """Capacity demand forecast"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    resource_id: str = ""
    resource_name: str = ""
    
    # Forecast details
    forecast_date: datetime = field(default_factory=datetime.now)
    forecast_period_months: int = 12
    forecast_method: str = "Trend Analysis"
    
    # Historical data used
    historical_period_months: int = 6
    data_points_used: int = 0
    
    # Forecast results
    current_baseline: float = 0.0
    projected_growth_rate: float = 0.0  # Monthly growth rate
    forecasted_values: List[Tuple[datetime, float]] = field(default_factory=list)
    
    # Confidence and accuracy
    confidence_level: float = 85.0  # Percentage
    margin_of_error: float = 10.0  # Percentage
    
    # Capacity recommendations
    recommended_action: str = ""
    capacity_breach_date: Optional[datetime] = None
    additional_capacity_needed: float = 0.0
    
    def calculate_capacity_exhaustion_date(self, capacity_limit: float) -> Optional[datetime]:
        """Calculate when capacity will be exhausted"""
        
        if self.projected_growth_rate <= 0:
            return None
        
        months_to_exhaustion = (capacity_limit - self.current_baseline) / self.projected_growth_rate
        
        if months_to_exhaustion <= 0:
            return datetime.now()  # Already at capacity
        
        return datetime.now() + timedelta(days=months_to_exhaustion * 30)
    
    def get_forecasted_value(self, target_date: datetime) -> float:
        """Get forecasted value for a specific date"""
        
        months_from_now = (target_date - datetime.now()).days / 30.44
        return self.current_baseline + (self.projected_growth_rate * months_from_now)


@dataclass
class CapacityPlan:
    """Capacity planning document"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    plan_name: str = ""
    plan_type: CapacityPlanType = CapacityPlanType.PROACTIVE
    
    # Planning scope
    services_covered: List[str] = field(default_factory=list)
    resources_covered: List[str] = field(default_factory=list)
    planning_horizon_months: int = 12
    
    # Plan details
    created_date: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    approved_by: str = ""
    review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    
    # Business context
    business_drivers: List[str] = field(default_factory=list)
    expected_business_changes: List[str] = field(default_factory=list)
    budget_constraints: Dict[str, Any] = field(default_factory=dict)
    
    # Capacity recommendations
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    investment_required: Decimal = Decimal('0.00')
    expected_benefits: List[str] = field(default_factory=list)
    
    # Implementation timeline
    implementation_phases: List[Dict[str, Any]] = field(default_factory=list)
    risk_assessment: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_recommendation(self, resource_id: str, action: str, 
                         justification: str, cost: Decimal, timeline: str):
        """Add a capacity recommendation"""
        
        recommendation = {
            "resource_id": resource_id,
            "action": action,
            "justification": justification,
            "estimated_cost": str(cost),
            "implementation_timeline": timeline,
            "priority": "Medium",
            "status": "Proposed"
        }
        
        self.recommendations.append(recommendation)
        self.investment_required += cost
    
    def get_high_priority_recommendations(self) -> List[Dict[str, Any]]:
        """Get high priority recommendations"""
        return [r for r in self.recommendations if r.get("priority") == "High"]


@dataclass
class ResourceCapacity:
    """Resource capacity definition and current status"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    resource_name: str = ""
    resource_type: ResourceType = ResourceType.CPU
    
    # Capacity specifications
    total_capacity: float = 100.0
    available_capacity: float = 100.0
    allocated_capacity: float = 0.0
    reserved_capacity: float = 0.0  # Buffer capacity
    
    # Units and measurement
    capacity_unit: str = ""
    measurement_method: str = ""
    
    # Scaling information
    scaling_strategy: ScalingStrategy = ScalingStrategy.VERTICAL
    minimum_capacity: float = 0.0
    maximum_capacity: float = 100.0
    scaling_increment: float = 10.0
    
    # Current performance
    current_utilization: float = 0.0
    peak_utilization: float = 0.0
    average_utilization: float = 0.0
    
    # Associated services
    dependent_services: List[str] = field(default_factory=list)
    
    # Metadata
    last_updated: datetime = field(default_factory=datetime.now)
    
    def get_utilization_percentage(self) -> float:
        """Calculate current utilization percentage"""
        if self.total_capacity == 0:
            return 0.0
        return (self.allocated_capacity / self.total_capacity) * 100
    
    def get_available_percentage(self) -> float:
        """Calculate available capacity percentage"""
        if self.total_capacity == 0:
            return 0.0
        return (self.available_capacity / self.total_capacity) * 100
    
    def can_allocate(self, requested_capacity: float) -> bool:
        """Check if requested capacity can be allocated"""
        return self.available_capacity >= requested_capacity
    
    def allocate_capacity(self, amount: float) -> bool:
        """Allocate capacity if available"""
        if self.can_allocate(amount):
            self.allocated_capacity += amount
            self.available_capacity -= amount
            self.last_updated = datetime.now()
            return True
        return False
    
    def release_capacity(self, amount: float) -> bool:
        """Release allocated capacity"""
        if self.allocated_capacity >= amount:
            self.allocated_capacity -= amount
            self.available_capacity += amount
            self.last_updated = datetime.now()
            return True
        return False


class PerformanceMonitor:
    """Real-time performance and capacity monitoring"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.monitored_resources: Dict[str, ResourceCapacity] = {}
        self.monitoring_active = False
        self.recent_metrics: Dict[str, List[PerformanceMetric]] = defaultdict(list)
        
    def add_resource_monitor(self, resource: ResourceCapacity):
        """Add a resource to monitoring"""
        
        self.monitored_resources[resource.id] = resource
        self.logger.info(f"Added resource {resource.resource_name} to capacity monitoring")
    
    async def collect_performance_metrics(self) -> List[PerformanceMetric]:
        """Collect performance metrics from all monitored resources"""
        
        metrics = []
        current_time = datetime.now()
        
        for resource_id, resource in self.monitored_resources.items():
            # Simulate metric collection - in real implementation, this would:
            # - Query monitoring systems (Prometheus, CloudWatch, etc.)
            # - Collect OS-level metrics
            # - Query application performance counters
            # - Get database performance statistics
            
            # Generate realistic utilization patterns
            base_utilization = 45 + (hash(resource_id) % 30)  # 45-75% base
            time_factor = math.sin((current_time.hour * 60 + current_time.minute) * math.pi / 720)  # Daily pattern
            random_factor = (hash(str(current_time)) % 20 - 10) / 10  # ±10% random
            
            current_util = max(0, min(100, base_utilization + (time_factor * 20) + random_factor))
            
            # CPU utilization
            cpu_metric = PerformanceMetric(
                resource_id=resource_id,
                resource_name=resource.resource_name,
                metric_type=CapacityMetricType.UTILIZATION,
                value=current_util,
                unit="%",
                measurement_source="System Monitor",
                concurrent_users=hash(resource_id) % 100 + 50,
                transaction_count=int(current_util * 10)
            )
            
            # Memory utilization (usually higher than CPU)
            memory_metric = PerformanceMetric(
                resource_id=resource_id,
                resource_name=f"{resource.resource_name} Memory",
                metric_type=CapacityMetricType.UTILIZATION,
                value=min(100, current_util + 15),
                unit="%",
                measurement_source="System Monitor"
            )
            
            # Response time (inverse relationship with utilization)
            response_time = max(50, 200 - (current_util * 1.5)) + (hash(str(current_time)) % 100)
            response_metric = PerformanceMetric(
                resource_id=resource_id,
                resource_name=resource.resource_name,
                metric_type=CapacityMetricType.RESPONSE_TIME,
                value=response_time,
                unit="ms",
                measurement_source="Application Monitor"
            )
            
            metrics.extend([cpu_metric, memory_metric, response_metric])
            
            # Update resource utilization
            resource.current_utilization = current_util
            resource.peak_utilization = max(resource.peak_utilization, current_util)
            
            # Keep recent metrics for trending
            self.recent_metrics[resource_id].append(cpu_metric)
            if len(self.recent_metrics[resource_id]) > 100:  # Keep last 100 readings
                self.recent_metrics[resource_id] = self.recent_metrics[resource_id][-100:]
            
            # Calculate average utilization
            if self.recent_metrics[resource_id]:
                resource.average_utilization = statistics.mean([
                    m.value for m in self.recent_metrics[resource_id][-20:]  # Last 20 readings
                ])
        
        return metrics
    
    async def start_monitoring(self):
        """Start continuous performance monitoring"""
        
        self.monitoring_active = True
        self.logger.info("Started capacity monitoring")
        
        while self.monitoring_active:
            await self.collect_performance_metrics()
            await asyncio.sleep(60)  # Collect metrics every minute
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        self.logger.info("Stopped capacity monitoring")
    
    def get_resource_metrics(self, resource_id: str, 
                           hours: int = 24) -> List[PerformanceMetric]:
        """Get recent metrics for a resource"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            m for m in self.recent_metrics.get(resource_id, [])
            if m.timestamp >= cutoff_time
        ]
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        
        status = {
            "monitoring_active": self.monitoring_active,
            "monitored_resources": len(self.monitored_resources),
            "resources": {}
        }
        
        for resource_id, resource in self.monitored_resources.items():
            recent_metrics = self.get_resource_metrics(resource_id, 1)  # Last hour
            
            status["resources"][resource_id] = {
                "name": resource.resource_name,
                "type": resource.resource_type.value,
                "current_utilization": resource.current_utilization,
                "average_utilization": resource.average_utilization,
                "peak_utilization": resource.peak_utilization,
                "total_capacity": resource.total_capacity,
                "available_capacity": resource.available_capacity,
                "recent_metrics_count": len(recent_metrics)
            }
        
        return status


class CapacityAnalyzer:
    """Advanced capacity analysis and forecasting"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_trends(self, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Analyze performance trends from metrics"""
        
        if len(metrics) < 10:
            return {"error": "Insufficient data for trend analysis"}
        
        # Sort metrics by timestamp
        sorted_metrics = sorted(metrics, key=lambda x: x.timestamp)
        
        # Calculate trend statistics
        values = [m.value for m in sorted_metrics]
        
        # Simple linear regression for trend
        n = len(values)
        x_values = list(range(n))
        
        # Calculate slope (trend direction)
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(values)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        trend_slope = numerator / denominator if denominator != 0 else 0
        
        # Trend analysis
        analysis = {
            "data_points": n,
            "time_span_hours": (sorted_metrics[-1].timestamp - sorted_metrics[0].timestamp).total_seconds() / 3600,
            "current_value": values[-1],
            "average_value": y_mean,
            "minimum_value": min(values),
            "maximum_value": max(values),
            "standard_deviation": statistics.stdev(values) if n > 1 else 0,
            "trend_slope": trend_slope,
            "trend_direction": "Increasing" if trend_slope > 0.1 else "Decreasing" if trend_slope < -0.1 else "Stable",
            "volatility": statistics.stdev(values) / y_mean * 100 if y_mean > 0 else 0
        }
        
        # Capacity utilization bands
        if sorted_metrics[0].metric_type == CapacityMetricType.UTILIZATION:
            analysis["utilization_bands"] = {
                "low_utilization_percent": len([v for v in values if v < 30]) / n * 100,
                "normal_utilization_percent": len([v for v in values if 30 <= v < 70]) / n * 100,
                "high_utilization_percent": len([v for v in values if 70 <= v < 90]) / n * 100,
                "critical_utilization_percent": len([v for v in values if v >= 90]) / n * 100
            }
        
        return analysis
    
    def create_capacity_forecast(self, resource_id: str, resource_name: str,
                               historical_metrics: List[PerformanceMetric],
                               forecast_months: int = 12) -> CapacityForecast:
        """Create capacity demand forecast"""
        
        if len(historical_metrics) < 30:  # Need at least 30 data points
            return CapacityForecast(
                resource_id=resource_id,
                resource_name=resource_name,
                forecast_period_months=forecast_months,
                recommended_action="Insufficient historical data for forecasting"
            )
        
        # Analyze historical trends
        trend_analysis = self.analyze_trends(historical_metrics)
        
        if "error" in trend_analysis:
            return CapacityForecast(
                resource_id=resource_id,
                resource_name=resource_name,
                recommended_action="Unable to analyze trends"
            )
        
        # Create forecast
        forecast = CapacityForecast(
            resource_id=resource_id,
            resource_name=resource_name,
            forecast_period_months=forecast_months,
            historical_period_months=6,
            data_points_used=len(historical_metrics),
            current_baseline=trend_analysis["current_value"],
            projected_growth_rate=trend_analysis["trend_slope"] * 30,  # Monthly growth
            confidence_level=max(50, 90 - trend_analysis["volatility"])  # Lower confidence for volatile data
        )
        
        # Generate monthly forecasted values
        for month in range(1, forecast_months + 1):
            forecast_date = datetime.now() + timedelta(days=month * 30)
            forecasted_value = forecast.get_forecasted_value(forecast_date)
            forecast.forecasted_values.append((forecast_date, forecasted_value))
        
        # Determine when capacity might be breached (assuming 90% threshold)
        capacity_limit = 90.0
        breach_date = forecast.calculate_capacity_exhaustion_date(capacity_limit)
        
        if breach_date and breach_date <= datetime.now() + timedelta(days=365):
            forecast.capacity_breach_date = breach_date
            forecast.additional_capacity_needed = forecasted_value - capacity_limit
            
            if breach_date <= datetime.now() + timedelta(days=90):
                forecast.recommended_action = "URGENT: Capacity expansion needed within 3 months"
            elif breach_date <= datetime.now() + timedelta(days=180):
                forecast.recommended_action = "Plan capacity expansion within 6 months"
            else:
                forecast.recommended_action = "Monitor and plan capacity expansion within 12 months"
        else:
            forecast.recommended_action = "Current capacity adequate for forecast period"
        
        return forecast
    
    def identify_bottlenecks(self, resource_metrics: Dict[str, List[PerformanceMetric]]) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks across resources"""
        
        bottlenecks = []
        
        for resource_id, metrics in resource_metrics.items():
            if not metrics:
                continue
            
            trend_analysis = self.analyze_trends(metrics)
            
            if "error" in trend_analysis:
                continue
            
            # Identify bottleneck conditions
            is_bottleneck = False
            bottleneck_reasons = []
            severity = "Low"
            
            # High utilization
            if trend_analysis["average_value"] > 80:
                is_bottleneck = True
                bottleneck_reasons.append(f"High average utilization: {trend_analysis['average_value']:.1f}%")
                severity = "Critical" if trend_analysis["average_value"] > 90 else "High"
            
            # High peak utilization
            if trend_analysis["maximum_value"] > 95:
                is_bottleneck = True
                bottleneck_reasons.append(f"Peak utilization exceeded 95%: {trend_analysis['maximum_value']:.1f}%")
                severity = "Critical"
            
            # Increasing trend with high utilization
            if (trend_analysis["trend_direction"] == "Increasing" and 
                trend_analysis["current_value"] > 70):
                is_bottleneck = True
                bottleneck_reasons.append(f"Increasing utilization trend: {trend_analysis['trend_slope']:.2f}% per hour")
                if severity == "Low":
                    severity = "Medium"
            
            # High volatility with high average
            if (trend_analysis["volatility"] > 25 and 
                trend_analysis["average_value"] > 60):
                is_bottleneck = True
                bottleneck_reasons.append(f"High volatility: {trend_analysis['volatility']:.1f}%")
                if severity == "Low":
                    severity = "Medium"
            
            if is_bottleneck:
                bottleneck = {
                    "resource_id": resource_id,
                    "resource_name": metrics[0].resource_name if metrics else "Unknown",
                    "severity": severity,
                    "current_utilization": trend_analysis["current_value"],
                    "average_utilization": trend_analysis["average_value"],
                    "peak_utilization": trend_analysis["maximum_value"],
                    "trend_direction": trend_analysis["trend_direction"],
                    "reasons": bottleneck_reasons,
                    "impact": "High" if severity == "Critical" else "Medium",
                    "recommended_actions": self._get_bottleneck_recommendations(trend_analysis, severity)
                }
                
                bottlenecks.append(bottleneck)
        
        # Sort by severity
        severity_order = {"Critical": 3, "High": 2, "Medium": 1, "Low": 0}
        bottlenecks.sort(key=lambda x: severity_order.get(x["severity"], 0), reverse=True)
        
        return bottlenecks
    
    def _get_bottleneck_recommendations(self, trend_analysis: Dict[str, Any], 
                                      severity: str) -> List[str]:
        """Get recommendations for addressing bottlenecks"""
        
        recommendations = []
        
        if severity == "Critical":
            recommendations.append("Immediate capacity expansion required")
            recommendations.append("Implement load balancing or scaling")
            recommendations.append("Review and optimize high-usage processes")
        
        elif severity == "High":
            recommendations.append("Plan capacity upgrade within 1-2 months")
            recommendations.append("Optimize resource allocation")
            recommendations.append("Implement performance monitoring alerts")
        
        elif severity == "Medium":
            recommendations.append("Monitor closely and plan capacity review")
            recommendations.append("Analyze usage patterns for optimization opportunities")
            recommendations.append("Consider workload distribution improvements")
        
        # Trend-specific recommendations
        if trend_analysis["trend_direction"] == "Increasing":
            recommendations.append("Investigate root cause of increasing demand")
            recommendations.append("Implement predictive scaling if available")
        
        if trend_analysis["volatility"] > 25:
            recommendations.append("Analyze usage patterns to understand volatility")
            recommendations.append("Consider implementing elastic scaling")
        
        return recommendations


class CapacityManager:
    """Main Capacity Management system"""
    
    def __init__(self):
        self.resources: Dict[str, ResourceCapacity] = {}
        self.thresholds: Dict[str, List[CapacityThreshold]] = defaultdict(list)
        self.plans: Dict[str, CapacityPlan] = {}
        self.forecasts: Dict[str, CapacityForecast] = {}
        self.monitor = PerformanceMonitor()
        self.analyzer = CapacityAnalyzer()
        self.logger = logging.getLogger(__name__)
        
        # Metrics storage
        self.historical_metrics: Dict[str, List[PerformanceMetric]] = defaultdict(list)
        
        # Statistics
        self.stats = {
            "total_resources": 0,
            "resources_over_threshold": 0,
            "average_utilization": 0.0,
            "resources_requiring_attention": 0,
            "active_forecasts": 0,
            "capacity_plans": 0
        }
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample capacity data"""
        
        # Sample resources
        web_server_capacity = ResourceCapacity(
            resource_name="Web Server Cluster",
            resource_type=ResourceType.CPU,
            total_capacity=100.0,
            available_capacity=35.0,
            allocated_capacity=65.0,
            reserved_capacity=10.0,
            capacity_unit="%",
            scaling_strategy=ScalingStrategy.HORIZONTAL,
            minimum_capacity=20.0,
            maximum_capacity=200.0,
            scaling_increment=25.0,
            dependent_services=["Customer Portal", "API Gateway"]
        )
        
        database_capacity = ResourceCapacity(
            resource_name="Database Server",
            resource_type=ResourceType.MEMORY,
            total_capacity=64.0,
            available_capacity=16.0,
            allocated_capacity=48.0,
            reserved_capacity=8.0,
            capacity_unit="GB",
            scaling_strategy=ScalingStrategy.VERTICAL,
            minimum_capacity=32.0,
            maximum_capacity=256.0,
            scaling_increment=32.0,
            dependent_services=["Customer Database", "Analytics"]
        )
        
        storage_capacity = ResourceCapacity(
            resource_name="Primary Storage",
            resource_type=ResourceType.STORAGE,
            total_capacity=10000.0,
            available_capacity=3500.0,
            allocated_capacity=6500.0,
            reserved_capacity=500.0,
            capacity_unit="GB",
            scaling_strategy=ScalingStrategy.VERTICAL,
            minimum_capacity=5000.0,
            maximum_capacity=50000.0,
            scaling_increment=1000.0,
            dependent_services=["All Services"]
        )
        
        network_capacity = ResourceCapacity(
            resource_name="Network Bandwidth",
            resource_type=ResourceType.NETWORK,
            total_capacity=1000.0,
            available_capacity=400.0,
            allocated_capacity=600.0,
            reserved_capacity=100.0,
            capacity_unit="Mbps",
            scaling_strategy=ScalingStrategy.HYBRID,
            minimum_capacity=500.0,
            maximum_capacity=10000.0,
            scaling_increment=500.0,
            dependent_services=["All Network Services"]
        )
        
        # Add resources
        self.add_resource(web_server_capacity)
        self.add_resource(database_capacity)
        self.add_resource(storage_capacity)
        self.add_resource(network_capacity)
        
        # Sample thresholds
        for resource_id, resource in self.resources.items():
            threshold = CapacityThreshold(
                resource_id=resource_id,
                resource_name=resource.resource_name,
                warning_threshold=70.0,
                critical_threshold=85.0,
                breach_threshold=95.0,
                warning_actions=["Send notification"],
                critical_actions=["Send alert", "Scale up if available"],
                breach_actions=["Send urgent alert", "Auto-scale", "Create incident"]
            )
            self.add_threshold(threshold)
        
        # Add resources to monitoring
        for resource in self.resources.values():
            self.monitor.add_resource_monitor(resource)
        
        # Generate sample historical metrics
        self._generate_sample_metrics()
        
        # Sample capacity plan
        sample_plan = CapacityPlan(
            plan_name="Q1 2026 Capacity Plan",
            plan_type=CapacityPlanType.PROACTIVE,
            services_covered=["Customer Portal", "Database Services", "API Gateway"],
            resources_covered=list(self.resources.keys()),
            planning_horizon_months=12,
            created_by="Capacity Manager",
            business_drivers=["Expected 25% user growth", "New product launch", "Peak season preparation"],
            expected_business_changes=["Launch of mobile app", "Expansion to new regions"],
            budget_constraints={"total_budget": "500000", "capital_expenditure": "300000"}
        )
        
        # Add sample recommendations
        sample_plan.add_recommendation(
            resource_id=list(self.resources.keys())[0],
            action="Add 2 additional web servers",
            justification="Handle expected 25% user growth",
            cost=Decimal('75000.00'),
            timeline="Q2 2026"
        )
        
        sample_plan.add_recommendation(
            resource_id=list(self.resources.keys())[1],
            action="Upgrade database memory to 128GB",
            justification="Support increased transaction volume",
            cost=Decimal('25000.00'),
            timeline="Q1 2026"
        )
        
        self.add_capacity_plan(sample_plan)
    
    def _generate_sample_metrics(self):
        """Generate sample historical metrics for demonstration"""
        
        # Generate 30 days of hourly metrics for each resource
        for resource_id, resource in self.resources.items():
            for days_ago in range(30, 0, -1):
                for hour in range(0, 24, 4):  # Every 4 hours
                    timestamp = datetime.now() - timedelta(days=days_ago, hours=hour)
                    
                    # Generate realistic utilization patterns
                    base_util = 40 + (hash(resource_id) % 30)  # 40-70% base
                    time_factor = math.sin(hour * math.pi / 12)  # Daily pattern
                    day_factor = 1 + (days_ago % 7) * 0.1  # Weekly pattern
                    
                    utilization = max(10, min(95, base_util + (time_factor * 25) * day_factor))
                    
                    metric = PerformanceMetric(
                        resource_id=resource_id,
                        resource_name=resource.resource_name,
                        metric_type=CapacityMetricType.UTILIZATION,
                        timestamp=timestamp,
                        value=utilization,
                        unit="%",
                        measurement_source="Historical Data"
                    )
                    
                    self.historical_metrics[resource_id].append(metric)
    
    def add_resource(self, resource: ResourceCapacity) -> str:
        """Add a resource to capacity management"""
        
        self.resources[resource.id] = resource
        self._update_statistics()
        
        self.logger.info(f"Added resource {resource.resource_name} to capacity management")
        return resource.id
    
    def get_resource(self, resource_id: str) -> Optional[ResourceCapacity]:
        """Get a resource by ID"""
        return self.resources.get(resource_id)
    
    def add_threshold(self, threshold: CapacityThreshold) -> str:
        """Add a capacity threshold"""
        
        self.thresholds[threshold.resource_id].append(threshold)
        
        self.logger.info(f"Added threshold for {threshold.resource_name}")
        return threshold.id
    
    def check_thresholds(self, resource_id: str, current_value: float) -> List[Dict[str, Any]]:
        """Check if current value breaches any thresholds"""
        
        breaches = []
        resource_thresholds = self.thresholds.get(resource_id, [])
        
        for threshold in resource_thresholds:
            if not threshold.active:
                continue
            
            breach_type = threshold.evaluate_threshold(current_value)
            if breach_type:
                breach = {
                    "threshold_id": threshold.id,
                    "resource_id": resource_id,
                    "resource_name": threshold.resource_name,
                    "breach_type": breach_type.value,
                    "current_value": current_value,
                    "threshold_value": getattr(threshold, f"{breach_type.value.lower()}_threshold"),
                    "status": threshold.get_threshold_status(current_value),
                    "actions": getattr(threshold, f"{breach_type.value.lower()}_actions"),
                    "timestamp": datetime.now()
                }
                breaches.append(breach)
        
        return breaches
    
    def add_capacity_plan(self, plan: CapacityPlan) -> str:
        """Add a capacity plan"""
        
        self.plans[plan.id] = plan
        self._update_statistics()
        
        self.logger.info(f"Added capacity plan {plan.plan_name}")
        return plan.id
    
    def create_capacity_forecast(self, resource_id: str, 
                               forecast_months: int = 12) -> Optional[CapacityForecast]:
        """Create capacity forecast for a resource"""
        
        resource = self.resources.get(resource_id)
        if not resource:
            return None
        
        historical_metrics = self.historical_metrics.get(resource_id, [])
        
        forecast = self.analyzer.create_capacity_forecast(
            resource_id=resource_id,
            resource_name=resource.resource_name,
            historical_metrics=historical_metrics,
            forecast_months=forecast_months
        )
        
        self.forecasts[resource_id] = forecast
        self._update_statistics()
        
        return forecast
    
    def analyze_bottlenecks(self) -> List[Dict[str, Any]]:
        """Analyze bottlenecks across all resources"""
        
        # Get recent metrics for all resources
        resource_metrics = {}
        for resource_id in self.resources.keys():
            resource_metrics[resource_id] = self.monitor.get_resource_metrics(resource_id, hours=24)
            
            # Include historical metrics if recent ones are limited
            if len(resource_metrics[resource_id]) < 10:
                resource_metrics[resource_id] = self.historical_metrics.get(resource_id, [])[-50:]
        
        return self.analyzer.identify_bottlenecks(resource_metrics)
    
    def get_capacity_dashboard(self) -> Dict[str, Any]:
        """Get capacity management dashboard data"""
        
        dashboard = {
            "generated_date": datetime.now().isoformat(),
            "summary": self.get_statistics(),
            "resource_status": {},
            "threshold_breaches": [],
            "bottlenecks": [],
            "forecasts": {},
            "monitoring_status": self.monitor.get_monitoring_status()
        }
        
        # Resource status
        for resource_id, resource in self.resources.items():
            utilization = resource.get_utilization_percentage()
            
            # Check current thresholds
            breaches = self.check_thresholds(resource_id, utilization)
            
            dashboard["resource_status"][resource_id] = {
                "name": resource.resource_name,
                "type": resource.resource_type.value,
                "utilization_percentage": utilization,
                "available_percentage": resource.get_available_percentage(),
                "current_utilization": resource.current_utilization,
                "average_utilization": resource.average_utilization,
                "peak_utilization": resource.peak_utilization,
                "scaling_strategy": resource.scaling_strategy.value,
                "threshold_status": "Normal" if not breaches else breaches[0]["breach_type"]
            }
            
            dashboard["threshold_breaches"].extend(breaches)
        
        # Bottleneck analysis
        dashboard["bottlenecks"] = self.analyze_bottlenecks()
        
        # Active forecasts
        for resource_id, forecast in self.forecasts.items():
            dashboard["forecasts"][resource_id] = {
                "resource_name": forecast.resource_name,
                "current_baseline": forecast.current_baseline,
                "projected_growth_rate": forecast.projected_growth_rate,
                "capacity_breach_date": forecast.capacity_breach_date.isoformat() if forecast.capacity_breach_date else None,
                "recommended_action": forecast.recommended_action,
                "confidence_level": forecast.confidence_level
            }
        
        return dashboard
    
    def generate_capacity_report(self, report_type: str = "summary") -> Dict[str, Any]:
        """Generate comprehensive capacity report"""
        
        if report_type == "summary":
            return self._generate_summary_report()
        elif report_type == "utilization":
            return self._generate_utilization_report()
        elif report_type == "forecasting":
            return self._generate_forecasting_report()
        elif report_type == "planning":
            return self._generate_planning_report()
        else:
            return {"error": "Unknown report type"}
    
    def _generate_summary_report(self) -> Dict[str, Any]:
        """Generate summary capacity report"""
        
        bottlenecks = self.analyze_bottlenecks()
        
        return {
            "report_type": "Capacity Summary",
            "generated_date": datetime.now().isoformat(),
            "statistics": self.get_statistics(),
            "resource_overview": {
                resource_id: {
                    "name": resource.resource_name,
                    "type": resource.resource_type.value,
                    "utilization": resource.get_utilization_percentage(),
                    "available": resource.get_available_percentage(),
                    "scaling_strategy": resource.scaling_strategy.value
                }
                for resource_id, resource in self.resources.items()
            },
            "bottlenecks": {
                "total_bottlenecks": len(bottlenecks),
                "critical_bottlenecks": len([b for b in bottlenecks if b["severity"] == "Critical"]),
                "high_bottlenecks": len([b for b in bottlenecks if b["severity"] == "High"]),
                "bottleneck_details": bottlenecks[:5]  # Top 5 bottlenecks
            },
            "capacity_health": {
                "overall_status": "Good" if len([b for b in bottlenecks if b["severity"] in ["Critical", "High"]]) == 0 else "Needs Attention",
                "resources_at_risk": len([r for r in self.resources.values() if r.get_utilization_percentage() > 80]),
                "resources_over_capacity": len([r for r in self.resources.values() if r.get_utilization_percentage() > 100])
            }
        }
    
    def _generate_utilization_report(self) -> Dict[str, Any]:
        """Generate detailed utilization report"""
        
        utilization_data = {}
        
        for resource_id, resource in self.resources.items():
            # Get recent metrics for trend analysis
            recent_metrics = self.monitor.get_resource_metrics(resource_id, hours=168)  # Last week
            if not recent_metrics:
                recent_metrics = self.historical_metrics.get(resource_id, [])[-50:]
            
            trend_analysis = self.analyzer.analyze_trends(recent_metrics) if recent_metrics else {}
            
            utilization_data[resource_id] = {
                "resource_name": resource.resource_name,
                "resource_type": resource.resource_type.value,
                "current_utilization": resource.current_utilization,
                "average_utilization": resource.average_utilization,
                "peak_utilization": resource.peak_utilization,
                "allocation_percentage": resource.get_utilization_percentage(),
                "available_percentage": resource.get_available_percentage(),
                "trend_analysis": trend_analysis,
                "capacity_details": {
                    "total_capacity": resource.total_capacity,
                    "allocated_capacity": resource.allocated_capacity,
                    "available_capacity": resource.available_capacity,
                    "reserved_capacity": resource.reserved_capacity,
                    "capacity_unit": resource.capacity_unit
                }
            }
        
        return {
            "report_type": "Utilization Report",
            "generated_date": datetime.now().isoformat(),
            "utilization_summary": {
                "average_utilization": statistics.mean([r.average_utilization for r in self.resources.values()]),
                "highest_utilization": max([r.current_utilization for r in self.resources.values()]),
                "lowest_utilization": min([r.current_utilization for r in self.resources.values()]),
                "resources_over_80_percent": len([r for r in self.resources.values() if r.current_utilization > 80])
            },
            "resource_utilization": utilization_data
        }
    
    def _generate_forecasting_report(self) -> Dict[str, Any]:
        """Generate capacity forecasting report"""
        
        # Create forecasts for all resources
        forecast_data = {}
        
        for resource_id, resource in self.resources.items():
            if resource_id not in self.forecasts:
                self.create_capacity_forecast(resource_id)
            
            forecast = self.forecasts.get(resource_id)
            if forecast:
                forecast_data[resource_id] = {
                    "resource_name": forecast.resource_name,
                    "current_baseline": forecast.current_baseline,
                    "projected_growth_rate": forecast.projected_growth_rate,
                    "forecast_period_months": forecast.forecast_period_months,
                    "confidence_level": forecast.confidence_level,
                    "capacity_breach_date": forecast.capacity_breach_date.isoformat() if forecast.capacity_breach_date else None,
                    "recommended_action": forecast.recommended_action,
                    "forecasted_values": [(date.isoformat(), value) for date, value in forecast.forecasted_values[:6]]  # Next 6 months
                }
        
        return {
            "report_type": "Capacity Forecasting Report",
            "generated_date": datetime.now().isoformat(),
            "forecasting_summary": {
                "total_forecasts": len(forecast_data),
                "resources_requiring_expansion": len([f for f in forecast_data.values() if f["capacity_breach_date"]]),
                "resources_with_urgent_needs": len([f for f in forecast_data.values() if f["recommended_action"].startswith("URGENT")]),
                "average_confidence": statistics.mean([f["confidence_level"] for f in forecast_data.values()]) if forecast_data else 0
            },
            "resource_forecasts": forecast_data
        }
    
    def _generate_planning_report(self) -> Dict[str, Any]:
        """Generate capacity planning report"""
        
        return {
            "report_type": "Capacity Planning Report",
            "generated_date": datetime.now().isoformat(),
            "planning_summary": {
                "total_plans": len(self.plans),
                "total_investment": str(sum([plan.investment_required for plan in self.plans.values()])),
                "active_plans": len([p for p in self.plans.values() if p.review_date is None or p.review_date > datetime.now()])
            },
            "capacity_plans": {
                plan_id: {
                    "plan_name": plan.plan_name,
                    "plan_type": plan.plan_type.value,
                    "planning_horizon_months": plan.planning_horizon_months,
                    "services_covered": plan.services_covered,
                    "investment_required": str(plan.investment_required),
                    "total_recommendations": len(plan.recommendations),
                    "high_priority_recommendations": len(plan.get_high_priority_recommendations()),
                    "business_drivers": plan.business_drivers,
                    "created_by": plan.created_by,
                    "created_date": plan.created_date.isoformat()
                }
                for plan_id, plan in self.plans.items()
            }
        }
    
    def _update_statistics(self):
        """Update capacity management statistics"""
        
        self.stats = {
            "total_resources": len(self.resources),
            "resources_over_threshold": 0,
            "average_utilization": 0.0,
            "resources_requiring_attention": 0,
            "active_forecasts": len(self.forecasts),
            "capacity_plans": len(self.plans)
        }
        
        if self.resources:
            utilizations = []
            
            for resource in self.resources.values():
                utilization = resource.current_utilization
                utilizations.append(utilization)
                
                # Check if over threshold (using 80% as default)
                if utilization > 80:
                    self.stats["resources_over_threshold"] += 1
                
                # Check if requiring attention (high utilization or trending up)
                if utilization > 70:
                    self.stats["resources_requiring_attention"] += 1
            
            self.stats["average_utilization"] = statistics.mean(utilizations)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current capacity management statistics"""
        return self.stats
    
    async def start_monitoring(self):
        """Start capacity monitoring"""
        await self.monitor.start_monitoring()
    
    def stop_monitoring(self):
        """Stop capacity monitoring"""
        self.monitor.stop_monitoring()


async def main():
    """Main function to demonstrate capacity management"""
    print("📊 ITIL 4 Capacity Management")
    print("=" * 50)
    
    # Initialize capacity manager
    capacity_mgr = CapacityManager()
    
    print("✅ Capacity Manager initialized with sample data")
    
    # Display statistics
    stats = capacity_mgr.get_statistics()
    print(f"\n📈 Capacity Management Statistics:")
    print(f"Total Resources: {stats['total_resources']}")
    print(f"Resources Over Threshold: {stats['resources_over_threshold']}")
    print(f"Average Utilization: {stats['average_utilization']:.1f}%")
    print(f"Resources Requiring Attention: {stats['resources_requiring_attention']}")
    print(f"Active Forecasts: {stats['active_forecasts']}")
    print(f"Capacity Plans: {stats['capacity_plans']}")
    
    # Show resource overview
    print(f"\n💾 Resource Overview:")
    for resource_id, resource in capacity_mgr.resources.items():
        utilization = resource.get_utilization_percentage()
        available = resource.get_available_percentage()
        status = "🔴" if utilization > 90 else "🟡" if utilization > 70 else "🟢"
        
        print(f"  {resource.resource_name} ({resource.resource_type.value}): {status}")
        print(f"    Allocated: {utilization:.1f}% | Available: {available:.1f}%")
        print(f"    Current Usage: {resource.current_utilization:.1f}%")
        print(f"    Peak Usage: {resource.peak_utilization:.1f}%")
        print(f"    Scaling: {resource.scaling_strategy.value}")
        print(f"    Capacity: {resource.allocated_capacity}/{resource.total_capacity} {resource.capacity_unit}")
    
    # Threshold analysis
    print(f"\n⚠️ Threshold Analysis:")
    total_breaches = 0
    for resource_id, resource in capacity_mgr.resources.items():
        current_util = resource.current_utilization
        breaches = capacity_mgr.check_thresholds(resource_id, current_util)
        
        if breaches:
            total_breaches += len(breaches)
            for breach in breaches:
                print(f"  {breach['resource_name']}: {breach['breach_type']} - {breach['status']}")
                print(f"    Actions: {', '.join(breach['actions'])}")
        else:
            print(f"  {resource.resource_name}: Normal - {current_util:.1f}% utilization")
    
    if total_breaches == 0:
        print("  All resources within normal thresholds ✅")
    
    # Bottleneck analysis
    print(f"\n🚧 Bottleneck Analysis:")
    bottlenecks = capacity_mgr.analyze_bottlenecks()
    
    if bottlenecks:
        print(f"Found {len(bottlenecks)} bottlenecks:")
        
        for bottleneck in bottlenecks[:5]:  # Show top 5
            print(f"\n  {bottleneck['resource_name']} ({bottleneck['severity']} Severity):")
            print(f"    Current: {bottleneck['current_utilization']:.1f}%")
            print(f"    Average: {bottleneck['average_utilization']:.1f}%")
            print(f"    Peak: {bottleneck['peak_utilization']:.1f}%")
            print(f"    Trend: {bottleneck['trend_direction']}")
            print(f"    Impact: {bottleneck['impact']}")
            
            print(f"    Reasons:")
            for reason in bottleneck['reasons']:
                print(f"      • {reason}")
            
            print(f"    Recommendations:")
            for rec in bottleneck['recommended_actions'][:3]:  # Top 3 recommendations
                print(f"      • {rec}")
    else:
        print("  No bottlenecks detected ✅")
    
    # Capacity forecasting
    print(f"\n🔮 Capacity Forecasting:")
    
    for resource_id in list(capacity_mgr.resources.keys())[:3]:  # First 3 resources
        forecast = capacity_mgr.create_capacity_forecast(resource_id, forecast_months=12)
        
        if forecast:
            resource_name = capacity_mgr.resources[resource_id].resource_name
            print(f"\n  {resource_name}:")
            print(f"    Current Baseline: {forecast.current_baseline:.1f}%")
            print(f"    Growth Rate: {forecast.projected_growth_rate:.2f}% per month")
            print(f"    Confidence: {forecast.confidence_level:.1f}%")
            print(f"    Recommendation: {forecast.recommended_action}")
            
            if forecast.capacity_breach_date:
                days_to_breach = (forecast.capacity_breach_date - datetime.now()).days
                print(f"    Capacity Breach: {days_to_breach} days ({forecast.capacity_breach_date.strftime('%Y-%m-%d')})")
            
            # Show next 3 months forecast
            print(f"    Next 3 Months:")
            for date, value in forecast.forecasted_values[:3]:
                print(f"      {date.strftime('%Y-%m')}: {value:.1f}%")
    
    # Capacity planning
    print(f"\n📋 Capacity Planning:")
    
    for plan_id, plan in capacity_mgr.plans.items():
        print(f"\n  {plan.plan_name} ({plan.plan_type.value}):")
        print(f"    Planning Horizon: {plan.planning_horizon_months} months")
        print(f"    Services: {', '.join(plan.services_covered)}")
        print(f"    Investment Required: ${plan.investment_required}")
        print(f"    Recommendations: {len(plan.recommendations)}")
        
        print(f"    Business Drivers:")
        for driver in plan.business_drivers:
            print(f"      • {driver}")
        
        if plan.recommendations:
            print(f"    Key Recommendations:")
            for rec in plan.recommendations[:3]:  # Top 3
                print(f"      • {rec['action']} - ${rec['estimated_cost']} ({rec['implementation_timeline']})")
    
    # Performance monitoring demo
    print(f"\n🔍 Performance Monitoring:")
    monitoring_status = capacity_mgr.monitor.get_monitoring_status()
    
    print(f"Monitoring Active: {'✅' if monitoring_status['monitoring_active'] else '❌'}")
    print(f"Monitored Resources: {monitoring_status['monitored_resources']}")
    
    print(f"\nResource Status:")
    for resource_id, resource_info in monitoring_status["resources"].items():
        print(f"  {resource_info['name']}:")
        print(f"    Current: {resource_info['current_utilization']:.1f}%")
        print(f"    Average: {resource_info['average_utilization']:.1f}%")
        print(f"    Peak: {resource_info['peak_utilization']:.1f}%")
        print(f"    Available: {resource_info['available_capacity']:.1f} {capacity_mgr.resources[resource_id].capacity_unit}")
    
    # Dashboard summary
    print(f"\n📊 Capacity Dashboard Summary:")
    dashboard = capacity_mgr.get_capacity_dashboard()
    
    print(f"Overall Health: {'🟢 Good' if stats['resources_over_threshold'] == 0 else '🟡 Needs Attention'}")
    print(f"Resources at Risk: {len([r for r in dashboard['resource_status'].values() if r['utilization_percentage'] > 80])}")
    print(f"Active Threshold Breaches: {len(dashboard['threshold_breaches'])}")
    print(f"Critical Bottlenecks: {len([b for b in dashboard['bottlenecks'] if b['severity'] == 'Critical'])}")
    
    # Utilization report
    print(f"\n📈 Utilization Report Summary:")
    util_report = capacity_mgr.generate_capacity_report("utilization")
    
    util_summary = util_report["utilization_summary"]
    print(f"Average Utilization: {util_summary['average_utilization']:.1f}%")
    print(f"Highest Utilization: {util_summary['highest_utilization']:.1f}%")
    print(f"Resources Over 80%: {util_summary['resources_over_80_percent']}")
    
    # Key recommendations
    print(f"\n🎯 Key Capacity Recommendations:")
    
    if bottlenecks:
        critical_bottlenecks = [b for b in bottlenecks if b["severity"] == "Critical"]
        if critical_bottlenecks:
            print("Critical Actions Required:")
            for bottleneck in critical_bottlenecks:
                print(f"  • {bottleneck['resource_name']}: {bottleneck['recommended_actions'][0]}")
    
    # Show forecasting recommendations
    urgent_forecasts = [f for f in capacity_mgr.forecasts.values() 
                       if f.recommended_action.startswith("URGENT")]
    
    if urgent_forecasts:
        print("Urgent Capacity Planning:")
        for forecast in urgent_forecasts:
            print(f"  • {forecast.resource_name}: {forecast.recommended_action}")
    
    if not bottlenecks and not urgent_forecasts:
        print("  Current capacity levels are adequate ✅")
        print("  Continue monitoring and regular capacity reviews")
    
    print(f"\n🎉 Capacity Management Demo Complete!")
    print("Key Features Demonstrated:")
    print("✅ Resource capacity tracking and monitoring")
    print("✅ Performance metrics collection and analysis")
    print("✅ Threshold management and alerting")
    print("✅ Bottleneck identification and analysis")
    print("✅ Capacity forecasting and trend analysis")
    print("✅ Capacity planning and recommendations")
    print("✅ Utilization reporting and optimization")
    print("✅ Real-time monitoring and dashboards")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())