"""
ITIL 4 Service Configuration Management Practice Implementation

This module provides comprehensive configuration management capabilities including:
- Configuration Management Database (CMDB)
- Configuration Item (CI) lifecycle management
- Relationship mapping and dependency tracking
- Change impact analysis
- Configuration baseline management
- Configuration auditing and compliance
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
from collections import defaultdict, deque
import networkx as nx

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.service_value_system import Priority, Status, Impact, Urgency, ConfigurationItem


class CIStatus(Enum):
    """Configuration Item status values"""
    PLANNED = "Planned"
    UNDER_DEVELOPMENT = "Under Development"
    LIVE = "Live"
    WITHDRAWN = "Withdrawn"
    DISPOSED = "Disposed"
    MAINTENANCE = "Under Maintenance"
    TESTING = "Under Testing"


class CIType(Enum):
    """Configuration Item types"""
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    SERVICE = "Service"
    PERSON = "Person"
    LOCATION = "Location"
    DOCUMENT = "Document"
    PROCESS = "Process"
    NETWORK = "Network"
    DATABASE = "Database"
    APPLICATION = "Application"
    VIRTUAL_MACHINE = "Virtual Machine"
    CONTAINER = "Container"
    CLOUD_RESOURCE = "Cloud Resource"


class RelationshipType(Enum):
    """Types of relationships between CIs"""
    DEPENDS_ON = "Depends On"
    SUPPORTS = "Supports"
    HOSTED_ON = "Hosted On"
    HOSTS = "Hosts"
    CONNECTED_TO = "Connected To"
    PART_OF = "Part Of"
    CONTAINS = "Contains"
    INSTALLED_ON = "Installed On"
    INSTALLS = "Installs"
    USES = "Uses"
    USED_BY = "Used By"
    MANAGES = "Manages"
    MANAGED_BY = "Managed By"
    BACKUP_OF = "Backup Of"
    BACKED_UP_BY = "Backed Up By"


class ChangeImpact(Enum):
    """Impact assessment levels for changes"""
    NONE = "None"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass
class ConfigurationItemExtended:
    """Extended Configuration Item with full CMDB capabilities"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: CIType = CIType.HARDWARE
    status: CIStatus = CIStatus.PLANNED
    environment: str = "Unknown"
    owner: Optional[str] = None
    custodian: Optional[str] = None
    location: Optional[str] = None
    cost_center: Optional[str] = None
    vendor: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    asset_tag: Optional[str] = None
    
    # Lifecycle dates
    created_date: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    install_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    end_of_life: Optional[datetime] = None
    
    # Technical attributes
    attributes: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    
    # Compliance and governance
    compliance_status: str = "Unknown"
    security_classification: str = "Public"
    data_classification: str = "Public"
    
    # Relationships
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    
    # Change tracking
    baseline_version: Optional[str] = None
    current_version: str = "1.0"
    change_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Monitoring and discovery
    discovery_source: Optional[str] = None
    last_discovered: Optional[datetime] = None
    monitoring_enabled: bool = False
    
    def add_relationship(self, target_ci_id: str, relationship_type: RelationshipType, 
                        attributes: Optional[Dict[str, Any]] = None):
        """Add a relationship to another CI"""
        relationship = {
            "target_ci_id": target_ci_id,
            "relationship_type": relationship_type.value,
            "created_date": datetime.now().isoformat(),
            "attributes": attributes or {}
        }
        self.relationships.append(relationship)
        self.last_modified = datetime.now()
    
    def remove_relationship(self, target_ci_id: str, relationship_type: RelationshipType):
        """Remove a relationship to another CI"""
        self.relationships = [
            rel for rel in self.relationships 
            if not (rel["target_ci_id"] == target_ci_id and 
                   rel["relationship_type"] == relationship_type.value)
        ]
        self.last_modified = datetime.now()
    
    def update_attribute(self, key: str, value: Any, change_reason: str = ""):
        """Update an attribute and track the change"""
        old_value = self.attributes.get(key)
        self.attributes[key] = value
        
        # Record change
        change_record = {
            "timestamp": datetime.now().isoformat(),
            "attribute": key,
            "old_value": old_value,
            "new_value": value,
            "change_reason": change_reason
        }
        self.change_history.append(change_record)
        self.last_modified = datetime.now()


@dataclass
class ConfigurationBaseline:
    """Represents a configuration baseline"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    version: str = "1.0"
    created_date: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    environment: str = ""
    ci_configurations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    approval_status: str = "Draft"
    approved_by: Optional[str] = None
    approved_date: Optional[datetime] = None


@dataclass
class ChangeImpactAssessment:
    """Results of change impact analysis"""
    change_id: str
    target_ci_id: str
    impact_level: ChangeImpact
    affected_cis: List[str]
    affected_services: List[str]
    risk_assessment: Dict[str, Any]
    recommendations: List[str]
    analysis_date: datetime = field(default_factory=datetime.now)
    analyzed_by: str = ""


class CMDB:
    """Configuration Management Database implementation"""
    
    def __init__(self):
        self.cis: Dict[str, ConfigurationItemExtended] = {}
        self.baselines: Dict[str, ConfigurationBaseline] = {}
        self.relationship_graph = nx.DiGraph()
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.stats = {
            "total_cis": 0,
            "cis_by_type": defaultdict(int),
            "cis_by_status": defaultdict(int),
            "total_relationships": 0
        }
    
    def add_ci(self, ci: ConfigurationItemExtended) -> str:
        """Add a CI to the CMDB"""
        self.cis[ci.id] = ci
        self.relationship_graph.add_node(ci.id, ci=ci)
        
        # Update statistics
        self.stats["total_cis"] += 1
        self.stats["cis_by_type"][ci.type.value] += 1
        self.stats["cis_by_status"][ci.status.value] += 1
        
        self.logger.info(f"Added CI {ci.id}: {ci.name}")
        return ci.id
    
    def get_ci(self, ci_id: str) -> Optional[ConfigurationItemExtended]:
        """Get a CI by ID"""
        return self.cis.get(ci_id)
    
    def update_ci(self, ci_id: str, updates: Dict[str, Any], change_reason: str = "") -> bool:
        """Update a CI with change tracking"""
        ci = self.cis.get(ci_id)
        if not ci:
            return False
        
        # Track changes
        for key, value in updates.items():
            if hasattr(ci, key):
                old_value = getattr(ci, key)
                setattr(ci, key, value)
                
                # Record change
                change_record = {
                    "timestamp": datetime.now().isoformat(),
                    "attribute": key,
                    "old_value": str(old_value) if old_value else None,
                    "new_value": str(value) if value else None,
                    "change_reason": change_reason
                }
                ci.change_history.append(change_record)
        
        ci.last_modified = datetime.now()
        self.logger.info(f"Updated CI {ci_id}: {change_reason}")
        return True
    
    def delete_ci(self, ci_id: str) -> bool:
        """Delete a CI from the CMDB"""
        if ci_id not in self.cis:
            return False
        
        ci = self.cis[ci_id]
        
        # Remove all relationships
        self.relationship_graph.remove_node(ci_id)
        
        # Update statistics
        self.stats["total_cis"] -= 1
        self.stats["cis_by_type"][ci.type.value] -= 1
        self.stats["cis_by_status"][ci.status.value] -= 1
        
        # Remove from storage
        del self.cis[ci_id]
        
        self.logger.info(f"Deleted CI {ci_id}: {ci.name}")
        return True
    
    def add_relationship(self, source_ci_id: str, target_ci_id: str, 
                        relationship_type: RelationshipType, 
                        attributes: Optional[Dict[str, Any]] = None) -> bool:
        """Add a relationship between two CIs"""
        
        if source_ci_id not in self.cis or target_ci_id not in self.cis:
            return False
        
        # Add to source CI
        source_ci = self.cis[source_ci_id]
        source_ci.add_relationship(target_ci_id, relationship_type, attributes)
        
        # Add to graph
        self.relationship_graph.add_edge(
            source_ci_id, 
            target_ci_id, 
            relationship_type=relationship_type.value,
            attributes=attributes or {}
        )
        
        self.stats["total_relationships"] += 1
        
        self.logger.info(f"Added relationship: {source_ci_id} -{relationship_type.value}-> {target_ci_id}")
        return True
    
    def remove_relationship(self, source_ci_id: str, target_ci_id: str, 
                           relationship_type: RelationshipType) -> bool:
        """Remove a relationship between two CIs"""
        
        if source_ci_id not in self.cis:
            return False
        
        # Remove from source CI
        source_ci = self.cis[source_ci_id]
        source_ci.remove_relationship(target_ci_id, relationship_type)
        
        # Remove from graph
        try:
            self.relationship_graph.remove_edge(source_ci_id, target_ci_id)
            self.stats["total_relationships"] -= 1
        except:
            pass  # Edge might not exist
        
        self.logger.info(f"Removed relationship: {source_ci_id} -{relationship_type.value}-> {target_ci_id}")
        return True
    
    def get_relationships(self, ci_id: str, relationship_type: Optional[RelationshipType] = None) -> List[Dict[str, Any]]:
        """Get relationships for a CI"""
        if ci_id not in self.cis:
            return []
        
        ci = self.cis[ci_id]
        
        if relationship_type:
            return [rel for rel in ci.relationships if rel["relationship_type"] == relationship_type.value]
        else:
            return ci.relationships
    
    def get_dependent_cis(self, ci_id: str, max_depth: int = 3) -> List[str]:
        """Get all CIs that depend on this CI"""
        if ci_id not in self.relationship_graph:
            return []
        
        dependent_cis = []
        
        try:
            # Find all nodes that can reach this CI (reverse dependencies)
            for node in self.relationship_graph.nodes():
                if node != ci_id:
                    try:
                        path = nx.shortest_path(self.relationship_graph, node, ci_id)
                        if len(path) <= max_depth + 1:  # +1 because path includes source and target
                            dependent_cis.append(node)
                    except nx.NetworkXNoPath:
                        continue
        except Exception as e:
            self.logger.error(f"Error finding dependent CIs: {e}")
        
        return dependent_cis
    
    def get_supporting_cis(self, ci_id: str, max_depth: int = 3) -> List[str]:
        """Get all CIs that this CI depends on"""
        if ci_id not in self.relationship_graph:
            return []
        
        supporting_cis = []
        
        try:
            # Find all nodes reachable from this CI
            for node in self.relationship_graph.nodes():
                if node != ci_id:
                    try:
                        path = nx.shortest_path(self.relationship_graph, ci_id, node)
                        if len(path) <= max_depth + 1:  # +1 because path includes source and target
                            supporting_cis.append(node)
                    except nx.NetworkXNoPath:
                        continue
        except Exception as e:
            self.logger.error(f"Error finding supporting CIs: {e}")
        
        return supporting_cis
    
    def search_cis(self, criteria: Dict[str, Any]) -> List[ConfigurationItemExtended]:
        """Search for CIs based on criteria"""
        results = []
        
        for ci in self.cis.values():
            match = True
            
            # Check basic attributes
            for key, value in criteria.items():
                if key == "type" and ci.type.value != value:
                    match = False
                    break
                elif key == "status" and ci.status.value != value:
                    match = False
                    break
                elif key == "environment" and ci.environment != value:
                    match = False
                    break
                elif key == "name" and value.lower() not in ci.name.lower():
                    match = False
                    break
                elif key == "owner" and ci.owner != value:
                    match = False
                    break
                elif key in ci.attributes and ci.attributes[key] != value:
                    match = False
                    break
            
            if match:
                results.append(ci)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get CMDB statistics"""
        return {
            **self.stats,
            "relationship_density": (self.stats["total_relationships"] / 
                                   max(self.stats["total_cis"], 1)),
            "average_relationships_per_ci": (self.stats["total_relationships"] / 
                                           max(self.stats["total_cis"], 1))
        }


class ConfigurationManager:
    """Main configuration management system"""
    
    def __init__(self):
        self.cmdb = CMDB()
        self.logger = logging.getLogger(__name__)
        
        # Load sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample configuration items"""
        
        # Sample CIs
        sample_cis = [
            {
                "name": "Production Web Server 01",
                "type": CIType.HARDWARE,
                "status": CIStatus.LIVE,
                "environment": "Production",
                "owner": "IT Operations",
                "location": "Data Center 1",
                "attributes": {
                    "cpu_cores": 8,
                    "memory_gb": 32,
                    "disk_gb": 500,
                    "ip_address": "10.1.1.10"
                }
            },
            {
                "name": "Customer Portal Application",
                "type": CIType.APPLICATION,
                "status": CIStatus.LIVE,
                "environment": "Production",
                "owner": "Development Team",
                "attributes": {
                    "version": "2.1.5",
                    "language": "Java",
                    "framework": "Spring Boot"
                }
            },
            {
                "name": "Production Database Server",
                "type": CIType.DATABASE,
                "status": CIStatus.LIVE,
                "environment": "Production",
                "owner": "Database Team",
                "location": "Data Center 1",
                "attributes": {
                    "database_type": "PostgreSQL",
                    "version": "13.4",
                    "size_gb": 1000
                }
            },
            {
                "name": "Load Balancer",
                "type": CIType.NETWORK,
                "status": CIStatus.LIVE,
                "environment": "Production",
                "owner": "Network Team",
                "attributes": {
                    "type": "F5 BigIP",
                    "virtual_ips": ["10.1.1.100", "10.1.1.101"]
                }
            }
        ]
        
        # Create CIs
        created_cis = []
        for ci_data in sample_cis:
            ci = ConfigurationItemExtended(**ci_data)
            ci_id = self.cmdb.add_ci(ci)
            created_cis.append(ci_id)
        
        # Create relationships
        if len(created_cis) >= 4:
            # Load balancer -> Web server
            self.cmdb.add_relationship(created_cis[3], created_cis[0], RelationshipType.CONNECTED_TO)
            
            # Web server -> Application
            self.cmdb.add_relationship(created_cis[0], created_cis[1], RelationshipType.HOSTS)
            
            # Application -> Database
            self.cmdb.add_relationship(created_cis[1], created_cis[2], RelationshipType.DEPENDS_ON)
    
    async def analyze_change_impact(self, change_id: str, target_ci_id: str, 
                                  change_description: str) -> ChangeImpactAssessment:
        """Analyze the impact of a proposed change"""
        
        target_ci = self.cmdb.get_ci(target_ci_id)
        if not target_ci:
            raise ValueError(f"CI {target_ci_id} not found")
        
        # Get dependent and supporting CIs
        dependent_cis = self.cmdb.get_dependent_cis(target_ci_id)
        supporting_cis = self.cmdb.get_supporting_cis(target_ci_id)
        
        # Combine all affected CIs
        affected_cis = list(set([target_ci_id] + dependent_cis + supporting_cis))
        
        # Identify affected services
        affected_services = []
        for ci_id in affected_cis:
            ci = self.cmdb.get_ci(ci_id)
            if ci and ci.type == CIType.SERVICE:
                affected_services.append(ci.name)
            elif ci and ci.type == CIType.APPLICATION:
                # Applications often represent services
                affected_services.append(ci.name)
        
        # Determine impact level
        impact_level = self._assess_impact_level(target_ci, affected_cis, change_description)
        
        # Generate risk assessment
        risk_assessment = self._assess_risks(target_ci, affected_cis, change_description)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(target_ci, impact_level, risk_assessment)
        
        assessment = ChangeImpactAssessment(
            change_id=change_id,
            target_ci_id=target_ci_id,
            impact_level=impact_level,
            affected_cis=affected_cis,
            affected_services=affected_services,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            analyzed_by="Configuration Manager"
        )
        
        self.logger.info(f"Completed change impact analysis for {change_id}")
        return assessment
    
    def _assess_impact_level(self, target_ci: ConfigurationItemExtended, 
                           affected_cis: List[str], change_description: str) -> ChangeImpact:
        """Assess the overall impact level of a change"""
        
        # Start with base impact based on CI criticality
        if target_ci.environment.lower() == "production":
            base_impact = ChangeImpact.MEDIUM
        else:
            base_impact = ChangeImpact.LOW
        
        # Increase impact based on number of affected CIs
        if len(affected_cis) > 10:
            base_impact = ChangeImpact.HIGH
        elif len(affected_cis) > 5:
            base_impact = ChangeImpact.MEDIUM
        
        # Increase impact for critical CI types
        if target_ci.type in [CIType.DATABASE, CIType.SERVICE]:
            if base_impact == ChangeImpact.LOW:
                base_impact = ChangeImpact.MEDIUM
            elif base_impact == ChangeImpact.MEDIUM:
                base_impact = ChangeImpact.HIGH
        
        # Check for risk keywords in change description
        high_risk_keywords = ["upgrade", "migration", "replacement", "major"]
        critical_risk_keywords = ["emergency", "critical", "urgent", "immediate"]
        
        change_lower = change_description.lower()
        
        if any(keyword in change_lower for keyword in critical_risk_keywords):
            base_impact = ChangeImpact.CRITICAL
        elif any(keyword in change_lower for keyword in high_risk_keywords):
            if base_impact in [ChangeImpact.LOW, ChangeImpact.MEDIUM]:
                base_impact = ChangeImpact.HIGH
        
        return base_impact
    
    def _assess_risks(self, target_ci: ConfigurationItemExtended, 
                     affected_cis: List[str], change_description: str) -> Dict[str, Any]:
        """Assess risks associated with the change"""
        
        risks = {
            "service_disruption": "Low",
            "data_loss": "Low", 
            "security": "Low",
            "performance": "Low",
            "rollback_complexity": "Low"
        }
        
        # Service disruption risk
        if target_ci.environment.lower() == "production":
            risks["service_disruption"] = "Medium"
            if len(affected_cis) > 5:
                risks["service_disruption"] = "High"
        
        # Data loss risk
        if target_ci.type in [CIType.DATABASE, CIType.APPLICATION]:
            risks["data_loss"] = "Medium"
            if "migration" in change_description.lower():
                risks["data_loss"] = "High"
        
        # Security risk
        if any(keyword in change_description.lower() 
               for keyword in ["security", "patch", "update", "upgrade"]):
            risks["security"] = "Medium"
        
        # Performance risk
        if target_ci.type in [CIType.DATABASE, CIType.APPLICATION, CIType.NETWORK]:
            risks["performance"] = "Medium"
        
        # Rollback complexity
        if len(affected_cis) > 3:
            risks["rollback_complexity"] = "Medium"
        if any(keyword in change_description.lower() 
               for keyword in ["migration", "upgrade", "replacement"]):
            risks["rollback_complexity"] = "High"
        
        return risks
    
    def _generate_recommendations(self, target_ci: ConfigurationItemExtended, 
                                impact_level: ChangeImpact, 
                                risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on impact analysis"""
        
        recommendations = []
        
        # General recommendations based on impact level
        if impact_level in [ChangeImpact.HIGH, ChangeImpact.CRITICAL]:
            recommendations.extend([
                "Schedule change during maintenance window",
                "Obtain CAB (Change Advisory Board) approval",
                "Prepare detailed rollback plan",
                "Notify all stakeholders in advance"
            ])
        
        if impact_level == ChangeImpact.CRITICAL:
            recommendations.extend([
                "Consider emergency change process",
                "Have technical experts on standby",
                "Implement additional monitoring"
            ])
        
        # Risk-specific recommendations
        if risk_assessment.get("service_disruption") in ["High", "Medium"]:
            recommendations.append("Consider implementing change in phases")
        
        if risk_assessment.get("data_loss") in ["High", "Medium"]:
            recommendations.extend([
                "Perform full data backup before change",
                "Verify backup integrity and recovery procedures"
            ])
        
        if risk_assessment.get("rollback_complexity") == "High":
            recommendations.extend([
                "Test rollback procedures in non-production environment",
                "Document step-by-step rollback instructions"
            ])
        
        # Environment-specific recommendations
        if target_ci.environment.lower() == "production":
            recommendations.append("Test change in staging environment first")
        
        return list(set(recommendations))  # Remove duplicates
    
    def create_baseline(self, name: str, description: str, environment: str, 
                       ci_ids: List[str], created_by: str) -> ConfigurationBaseline:
        """Create a configuration baseline"""
        
        baseline = ConfigurationBaseline(
            name=name,
            description=description,
            environment=environment,
            created_by=created_by
        )
        
        # Capture current configuration of specified CIs
        for ci_id in ci_ids:
            ci = self.cmdb.get_ci(ci_id)
            if ci:
                baseline.ci_configurations[ci_id] = {
                    "name": ci.name,
                    "type": ci.type.value,
                    "status": ci.status.value,
                    "attributes": ci.attributes.copy(),
                    "configuration": ci.configuration.copy(),
                    "version": ci.current_version,
                    "captured_at": datetime.now().isoformat()
                }
        
        self.cmdb.baselines[baseline.id] = baseline
        self.logger.info(f"Created baseline {baseline.id}: {name}")
        return baseline
    
    def compare_with_baseline(self, baseline_id: str, ci_id: str) -> Dict[str, Any]:
        """Compare current CI configuration with baseline"""
        
        baseline = self.cmdb.baselines.get(baseline_id)
        if not baseline or ci_id not in baseline.ci_configurations:
            return {"error": "Baseline or CI not found"}
        
        current_ci = self.cmdb.get_ci(ci_id)
        if not current_ci:
            return {"error": "Current CI not found"}
        
        baseline_config = baseline.ci_configurations[ci_id]
        
        differences = {
            "ci_id": ci_id,
            "baseline_id": baseline_id,
            "comparison_date": datetime.now().isoformat(),
            "changes": []
        }
        
        # Compare attributes
        current_attrs = current_ci.attributes
        baseline_attrs = baseline_config.get("attributes", {})
        
        # Check for changed attributes
        for key in set(current_attrs.keys()) | set(baseline_attrs.keys()):
            current_value = current_attrs.get(key)
            baseline_value = baseline_attrs.get(key)
            
            if current_value != baseline_value:
                differences["changes"].append({
                    "attribute": key,
                    "baseline_value": baseline_value,
                    "current_value": current_value,
                    "change_type": "modified" if key in baseline_attrs else "added"
                })
        
        # Compare basic properties
        for prop in ["status", "version"]:
            baseline_value = baseline_config.get(prop)
            current_value = getattr(current_ci, prop, None)
            if hasattr(current_ci, prop):
                current_value = getattr(current_ci, prop)
                if hasattr(current_value, 'value'):  # Handle enums
                    current_value = current_value.value
            
            if str(current_value) != str(baseline_value):
                differences["changes"].append({
                    "attribute": prop,
                    "baseline_value": baseline_value,
                    "current_value": current_value,
                    "change_type": "modified"
                })
        
        return differences
    
    def audit_configuration_compliance(self, environment: str = None) -> Dict[str, Any]:
        """Audit configuration compliance across the CMDB"""
        
        audit_results = {
            "audit_date": datetime.now().isoformat(),
            "environment": environment or "All",
            "total_cis_audited": 0,
            "compliance_issues": [],
            "summary": {
                "compliant": 0,
                "non_compliant": 0,
                "unknown": 0
            }
        }
        
        # Get CIs to audit
        if environment:
            cis_to_audit = [ci for ci in self.cmdb.cis.values() if ci.environment == environment]
        else:
            cis_to_audit = list(self.cmdb.cis.values())
        
        audit_results["total_cis_audited"] = len(cis_to_audit)
        
        for ci in cis_to_audit:
            compliance_status = self._check_ci_compliance(ci)
            
            if compliance_status["compliant"]:
                audit_results["summary"]["compliant"] += 1
            else:
                audit_results["summary"]["non_compliant"] += 1
                audit_results["compliance_issues"].append({
                    "ci_id": ci.id,
                    "ci_name": ci.name,
                    "issues": compliance_status["issues"]
                })
        
        return audit_results
    
    def _check_ci_compliance(self, ci: ConfigurationItemExtended) -> Dict[str, Any]:
        """Check compliance for a single CI"""
        
        compliance_result = {
            "compliant": True,
            "issues": []
        }
        
        # Check required attributes
        required_attributes = {
            CIType.HARDWARE: ["cpu_cores", "memory_gb"],
            CIType.APPLICATION: ["version"],
            CIType.DATABASE: ["database_type", "version"]
        }
        
        if ci.type in required_attributes:
            for required_attr in required_attributes[ci.type]:
                if required_attr not in ci.attributes:
                    compliance_result["compliant"] = False
                    compliance_result["issues"].append(
                        f"Missing required attribute: {required_attr}"
                    )
        
        # Check ownership
        if not ci.owner:
            compliance_result["compliant"] = False
            compliance_result["issues"].append("CI has no assigned owner")
        
        # Check last modified date (should be updated within 90 days for live CIs)
        if ci.status == CIStatus.LIVE:
            days_since_update = (datetime.now() - ci.last_modified).days
            if days_since_update > 90:
                compliance_result["compliant"] = False
                compliance_result["issues"].append(
                    f"CI not updated in {days_since_update} days"
                )
        
        return compliance_result


async def main():
    """Main function to demonstrate configuration management"""
    print("⚙️  ITIL 4 Service Configuration Management")
    print("=" * 50)
    
    # Initialize configuration manager
    config_manager = ConfigurationManager()
    
    print("✅ Configuration Manager initialized with sample data")
    
    # Display CMDB statistics
    stats = config_manager.cmdb.get_statistics()
    print(f"\n📊 CMDB Statistics:")
    print(f"Total CIs: {stats['total_cis']}")
    print(f"Total Relationships: {stats['total_relationships']}")
    print(f"Relationship Density: {stats['relationship_density']:.2f}")
    
    print(f"\nCIs by Type:")  
    for ci_type, count in stats['cis_by_type'].items():
        print(f"  {ci_type}: {count}")
    
    print(f"\nCIs by Status:")
    for status, count in stats['cis_by_status'].items():
        print(f"  {status}: {count}")
    
    # Demonstrate change impact analysis
    print(f"\n🔍 Change Impact Analysis Demo")
    
    # Get a CI for analysis
    web_server_ci = None
    for ci in config_manager.cmdb.cis.values():
        if "Web Server" in ci.name:
            web_server_ci = ci
            break
    
    if web_server_ci:
        print(f"Analyzing impact of upgrading: {web_server_ci.name}")
        
        impact_assessment = await config_manager.analyze_change_impact(
            change_id="CHG001",
            target_ci_id=web_server_ci.id,
            change_description="Upgrade web server OS to latest version"
        )
        
        print(f"Impact Level: {impact_assessment.impact_level.value}")
        print(f"Affected CIs: {len(impact_assessment.affected_cis)}")
        print(f"Affected Services: {', '.join(impact_assessment.affected_services) or 'None identified'}")
        
        print(f"\nRisk Assessment:")
        for risk_type, level in impact_assessment.risk_assessment.items():
            print(f"  {risk_type.replace('_', ' ').title()}: {level}")
        
        print(f"\nRecommendations:")
        for i, recommendation in enumerate(impact_assessment.recommendations, 1):
            print(f"  {i}. {recommendation}")
    
    # Demonstrate baseline management
    print(f"\n📸 Configuration Baseline Demo")
    
    # Create a baseline
    ci_ids = list(config_manager.cmdb.cis.keys())[:2]  # First 2 CIs
    baseline = config_manager.create_baseline(
        name="Production Baseline v1.0",
        description="Initial production environment baseline",
        environment="Production",
        ci_ids=ci_ids,
        created_by="Configuration Manager"
    )
    
    print(f"Created baseline: {baseline.name} with {len(ci_ids)} CIs")
    
    # Simulate a configuration change
    if ci_ids:
        test_ci = config_manager.cmdb.get_ci(ci_ids[0])
        if test_ci:
            # Update an attribute
            config_manager.cmdb.update_ci(
                ci_ids[0],
                {"attributes": {**test_ci.attributes, "memory_gb": 64}},
                "Memory upgrade"
            )
            print(f"Updated CI: {test_ci.name} - Memory upgraded to 64GB")
            
            # Compare with baseline
            comparison = config_manager.compare_with_baseline(baseline.id, ci_ids[0])
            print(f"\nBaseline Comparison:")
            if comparison.get("changes"):
                for change in comparison["changes"]:
                    print(f"  {change['attribute']}: {change['baseline_value']} -> {change['current_value']}")
            else:
                print("  No changes detected")
    
    # Demonstrate configuration audit
    print(f"\n🔍 Configuration Compliance Audit")
    
    audit_results = config_manager.audit_configuration_compliance("Production")
    print(f"Audited {audit_results['total_cis_audited']} CIs in Production environment")
    print(f"Compliant: {audit_results['summary']['compliant']}")
    print(f"Non-compliant: {audit_results['summary']['non_compliant']}")
    
    if audit_results["compliance_issues"]:
        print(f"\nCompliance Issues Found:")
        for issue in audit_results["compliance_issues"]:
            print(f"  {issue['ci_name']}:")
            for problem in issue["issues"]:
                print(f"    - {problem}")
    
    # Demonstrate CI search
    print(f"\n🔎 CI Search Demo")
    
    # Search for production CIs
    prod_cis = config_manager.cmdb.search_cis({"environment": "Production"})
    print(f"Found {len(prod_cis)} Production CIs:")
    for ci in prod_cis:
        print(f"  {ci.name} ({ci.type.value})")
    
    # Search for application CIs
    app_cis = config_manager.cmdb.search_cis({"type": "Application"})
    print(f"\nFound {len(app_cis)} Application CIs:")
    for ci in app_cis:
        print(f"  {ci.name} - Version: {ci.attributes.get('version', 'Unknown')}")
    
    # Demonstrate relationship analysis
    print(f"\n🔗 Relationship Analysis Demo")
    
    if web_server_ci:
        print(f"Analyzing relationships for: {web_server_ci.name}")
        
        dependent_cis = config_manager.cmdb.get_dependent_cis(web_server_ci.id)
        supporting_cis = config_manager.cmdb.get_supporting_cis(web_server_ci.id)
        
        print(f"Dependent CIs ({len(dependent_cis)}):")
        for ci_id in dependent_cis:
            ci = config_manager.cmdb.get_ci(ci_id)
            if ci:
                print(f"  {ci.name} ({ci.type.value})")
        
        print(f"Supporting CIs ({len(supporting_cis)}):")
        for ci_id in supporting_cis:
            ci = config_manager.cmdb.get_ci(ci_id)
            if ci:
                print(f"  {ci.name} ({ci.type.value})")
    
    print(f"\n🎉 Configuration Management Demo Complete!")
    print("Key Features Demonstrated:")
    print("✅ Complete CMDB implementation")
    print("✅ Change impact analysis")
    print("✅ Configuration baselines")
    print("✅ Compliance auditing")
    print("✅ Relationship mapping")
    print("✅ CI lifecycle management")


if __name__ == "__main__":
    asyncio.run(main())