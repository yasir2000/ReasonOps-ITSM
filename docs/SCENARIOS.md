# End-to-End Scenario Examples

> **Complete workflow examples** demonstrating ReasonOps ITSM with AI Agents from problem detection to resolution.

## Table of Contents
- [Scenario 1: Critical Production Outage](#scenario-1-critical-production-outage)
- [Scenario 2: Database Performance Degradation](#scenario-2-database-performance-degradation)
- [Scenario 3: Automated Security Incident Response](#scenario-3-automated-security-incident-response)
- [Scenario 4: Planned Infrastructure Migration](#scenario-4-planned-infrastructure-migration)
- [Scenario 5: Service Desk Automation](#scenario-5-service-desk-automation)
- [Scenario 6: Capacity Planning & Scaling](#scenario-6-capacity-planning--scaling)

---

## Scenario 1: Critical Production Outage

### 📊 **Situation**
**Time:** 3:47 AM  
**Alert:** Web application returning 503 errors  
**Impact:** 5,000+ customers unable to access service  
**Priority:** Critical

### 🎯 **Objective**
Restore service within 15 minutes to meet SLA, identify root cause, and prevent recurrence.

### 🔄 **Complete Workflow**

#### **Step 1: Incident Detection & Creation**

**Automated Alert → SDK**
```python
from reasonops_sdk import ReasonOpsClient
from datetime import datetime

client = ReasonOpsClient(base_url="http://localhost:8000")

# Monitoring system detects issue and creates incident
incident = client.create_incident({
    "title": "Production Web App - 503 Service Unavailable",
    "description": "Web application returning 503 errors. Multiple users reporting inability to access service.",
    "priority": "critical",
    "category": "availability",
    "affected_services": ["web-app-prod", "api-gateway"],
    "affected_users": 5000,
    "detected_at": datetime.now().isoformat(),
    "source": "automated_monitoring",
    "monitoring_data": {
        "error_rate": "98.5%",
        "response_time": "timeout",
        "server_status": "unhealthy",
        "load_balancer": "all_backends_down"
    }
})

print(f"✅ Incident created: {incident['id']}")
# Output: ✅ Incident created: INC-2025-001
```

#### **Step 2: AI-Powered Incident Analysis**

**Run Incident Analysis Agent**
```python
# AI Agent analyzes incident context
analysis_result = client.run_agents(
    agent_type="incident_analysis",
    context={
        "incident_id": incident['id'],
        "description": incident['description'],
        "priority": incident['priority'],
        "monitoring_data": incident['monitoring_data'],
        "recent_changes": True  # Check for recent deployments
    }
)

print("🤖 AI Analysis:")
print(f"Status: {analysis_result['status']}")
print(f"Confidence: {analysis_result['confidence']:.0%}")
print("\nRecommendations:")
for i, rec in enumerate(analysis_result['recommendations'], 1):
    print(f"{i}. {rec}")
```

**AI Output:**
```
🤖 AI Analysis:
Status: success
Confidence: 92%

Recommendations:
1. Recent deployment detected 15 minutes ago (v2.1.0)
2. Check application server logs for startup errors
3. Verify database connection pool status
4. Review load balancer health checks
5. Consider immediate rollback to v2.0.9 (last stable)
```

#### **Step 3: Root Cause Analysis**

**Deep Dive with RCA Agent**
```python
# Run root cause analysis
rca_result = client.run_agents(
    agent_type="root_cause",
    context={
        "incident_id": incident['id'],
        "symptoms": ["503_errors", "backend_unhealthy", "connection_timeout"],
        "timeline": "2025-10-22T03:32:00Z",  # Deployment time
        "related_changes": ["deploy-v2.1.0"],
        "infrastructure_state": {
            "app_servers": 6,
            "healthy_servers": 0,
            "database": "operational",
            "cache": "operational"
        }
    }
)

print("\n🔍 Root Cause Analysis:")
print(f"Primary Cause: {rca_result['primary_cause']}")
print(f"Contributing Factors: {', '.join(rca_result['contributing_factors'])}")
print(f"\nEvidence:")
for evidence in rca_result['evidence']:
    print(f"  - {evidence}")
```

**RCA Output:**
```
🔍 Root Cause Analysis:
Primary Cause: Configuration error in v2.1.0 deployment
Contributing Factors: Missing database connection string, Incorrect environment variable

Evidence:
  - All app servers failing health checks
  - Application logs show: "DATABASE_URL environment variable not set"
  - Deployment manifest missing env var definition
  - v2.0.9 had correct configuration
```

#### **Step 4: Immediate Resolution**

**Execute Rollback via CLI**
```bash
# Quick rollback using CLI
python cli.py agents:run resolution_action '{
    "incident_id": "INC-2025-001",
    "action": "rollback",
    "target_version": "v2.0.9",
    "reason": "Missing DATABASE_URL in v2.1.0",
    "approval": "emergency_authorization"
}'
```

**Parallel: Update Incident Status**
```python
# Update incident with resolution steps
client.update_incident(incident['id'], {
    "status": "in_progress",
    "assigned_to": "sre-oncall",
    "resolution_steps": [
        "Identified missing DATABASE_URL in v2.1.0",
        "Initiated rollback to v2.0.9",
        "Monitoring service recovery"
    ],
    "estimated_resolution": "2025-10-22T04:00:00Z"
})
```

#### **Step 5: Service Restoration Verification**

**Monitor Recovery**
```python
import time

# Wait for rollback completion
print("🔄 Rollback in progress...")
time.sleep(60)

# Verify service health
health_check = client.run_agents(
    agent_type="health_verification",
    context={
        "incident_id": incident['id'],
        "services": ["web-app-prod", "api-gateway"],
        "expected_state": "healthy"
    }
)

if health_check['all_healthy']:
    print("✅ Service restored successfully!")
    print(f"   - Error rate: {health_check['metrics']['error_rate']}")
    print(f"   - Response time: {health_check['metrics']['avg_response_time']}")
    print(f"   - Healthy servers: {health_check['metrics']['healthy_servers']}/6")
else:
    print("⚠️ Service still degraded, escalating...")
```

**Output:**
```
🔄 Rollback in progress...
✅ Service restored successfully!
   - Error rate: 0.2%
   - Response time: 145ms
   - Healthy servers: 6/6
```

#### **Step 6: Incident Resolution & Documentation**

**Close Incident with Complete Documentation**
```python
# Resolve incident
resolution = client.resolve_incident(incident['id'], {
    "resolution": "Rolled back deployment v2.1.0 to v2.0.9 due to missing DATABASE_URL environment variable",
    "root_cause": "Configuration error in deployment manifest",
    "resolution_time": "2025-10-22T03:59:00Z",
    "downtime_minutes": 12,
    "affected_users": 5000,
    "preventive_actions": [
        "Add DATABASE_URL validation to CI/CD pipeline",
        "Implement pre-deployment configuration checks",
        "Update deployment checklist",
        "Schedule post-mortem meeting"
    ],
    "lessons_learned": [
        "Need automated config validation before production deploy",
        "Emergency rollback procedure worked well",
        "AI analysis correctly identified recent deployment as cause"
    ]
})

print(f"\n✅ Incident {incident['id']} resolved")
print(f"   Downtime: {resolution['downtime_minutes']} minutes")
print(f"   SLA Status: {'✅ Met' if resolution['downtime_minutes'] < 15 else '❌ Missed'}")
```

#### **Step 7: Create Problem Record for Prevention**

**Link to Problem Management**
```python
# Create problem record to prevent recurrence
problem = client.create_problem({
    "title": "Deployment process lacks configuration validation",
    "description": "Missing environment variables not detected before production deployment",
    "related_incidents": [incident['id']],
    "root_cause": "No automated validation of required environment variables in CI/CD pipeline",
    "priority": "high",
    "impact": "Potential for production outages",
    "proposed_solutions": [
        {
            "solution": "Implement pre-deployment config checker",
            "effort": "2 days",
            "risk": "low",
            "benefit": "Prevent similar configuration errors"
        },
        {
            "solution": "Add smoke tests for environment variables",
            "effort": "1 day",
            "risk": "low",
            "benefit": "Early detection in staging environment"
        }
    ]
})

print(f"\n📋 Problem {problem['id']} created for long-term fix")
```

#### **Step 8: Create Change Request for Fix**

**Implement Permanent Solution**
```python
# Create change request for CI/CD improvement
change = client.create_change({
    "title": "Add configuration validation to deployment pipeline",
    "description": "Implement automated checks for required environment variables",
    "change_type": "standard",
    "category": "ci_cd_improvement",
    "risk_level": "low",
    "implementation_plan": [
        "Add config validation script to pipeline",
        "Define required env vars per environment",
        "Update deployment documentation",
        "Test in development environment",
        "Roll out to staging",
        "Deploy to production"
    ],
    "rollback_plan": "Remove validation step from pipeline",
    "testing_plan": "Simulate missing config and verify pipeline fails",
    "related_problem": problem['id'],
    "scheduled_date": "2025-10-25T10:00:00Z",
    "estimated_duration": "2 hours"
})

print(f"📝 Change {change['id']} scheduled for implementation")
```

### 📊 **Results & Metrics**

```python
# Generate incident report
report = client.generate_incident_report(incident['id'])

print("\n" + "="*60)
print("📊 INCIDENT SUMMARY REPORT")
print("="*60)
print(f"Incident ID: {report['id']}")
print(f"Title: {report['title']}")
print(f"Priority: {report['priority']}")
print(f"Detection: {report['detected_at']}")
print(f"Resolution: {report['resolved_at']}")
print(f"Total Downtime: {report['downtime_minutes']} minutes")
print(f"Affected Users: {report['affected_users']:,}")
print(f"SLA Compliance: {'✅ Yes' if report['sla_met'] else '❌ No'}")
print(f"\nAI Contribution:")
print(f"  - Analysis Time: {report['ai_analysis_time']}s")
print(f"  - Recommendations Used: {report['ai_recommendations_applied']}/5")
print(f"  - Accuracy: {report['ai_accuracy']:.0%}")
print(f"\nFollow-up Actions:")
print(f"  - Problem Created: {problem['id']}")
print(f"  - Change Scheduled: {change['id']}")
print("="*60)
```

**Output:**
```
============================================================
📊 INCIDENT SUMMARY REPORT
============================================================
Incident ID: INC-2025-001
Title: Production Web App - 503 Service Unavailable
Priority: critical
Detection: 2025-10-22T03:47:00Z
Resolution: 2025-10-22T03:59:00Z
Total Downtime: 12 minutes
Affected Users: 5,000
SLA Compliance: ✅ Yes

AI Contribution:
  - Analysis Time: 2.3s
  - Recommendations Used: 4/5
  - Accuracy: 92%

Follow-up Actions:
  - Problem Created: PRB-2025-042
  - Change Scheduled: CHG-2025-156
============================================================
```

### 🎯 **Key Takeaways**

1. **Speed:** AI analysis identified root cause in 2.3 seconds
2. **Accuracy:** 92% confidence, correct recommendation for rollback
3. **SLA Compliance:** 12-minute resolution (3 minutes under 15-minute SLA)
4. **Automation:** End-to-end workflow from detection to resolution
5. **Prevention:** Problem and Change records created for long-term fix

---

## Scenario 2: Database Performance Degradation

### 📊 **Situation**
**Time:** 2:15 PM  
**Alert:** Database query response time increased by 400%  
**Impact:** API endpoints timing out, slow user experience  
**Priority:** High

### 🎯 **Objective**
Identify performance bottleneck, optimize queries, and restore normal response times.

### 🔄 **Complete Workflow**

#### **Step 1: Performance Monitoring Detection**

**Web UI: Real-time Dashboard Alert**
```typescript
// User sees alert on AgentsPage dashboard
// Health Status showing degraded database performance
```

**Create Incident via Web UI:**
1. Navigate to http://localhost:5173/incidents
2. Click "Create Incident"
3. Fill form:
   - Title: "Database Performance Degradation - Slow Queries"
   - Priority: High
   - Category: Performance
   - Description: "Database response time increased from 50ms to 250ms average"

**Or via API:**
```bash
curl -X POST http://localhost:8000/api/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Database Performance Degradation - Slow Queries",
    "priority": "high",
    "category": "performance",
    "description": "Database response time increased from 50ms to 250ms average",
    "metrics": {
      "baseline_response_time": "50ms",
      "current_response_time": "250ms",
      "degradation": "400%",
      "affected_queries": ["user_search", "order_history", "product_catalog"]
    }
  }'
```

#### **Step 2: AI-Powered Performance Analysis**

**CLI: Run Performance Analysis**
```bash
python cli.py agents:run performance_analysis '{
    "incident_id": "INC-2025-002",
    "metric_type": "database_response_time",
    "baseline": 50,
    "current": 250,
    "time_window": "last_2_hours",
    "affected_queries": ["user_search", "order_history", "product_catalog"]
}'
```

**AI Analysis Output:**
```json
{
  "status": "success",
  "analysis": {
    "primary_issue": "Missing database index on users.email column",
    "severity": "high",
    "confidence": 0.89,
    "evidence": [
      "EXPLAIN ANALYZE shows full table scan on users table",
      "users table has 2.5M rows",
      "user_search query runs 15,000 times/hour",
      "No index on email column (used in WHERE clause)"
    ],
    "recommendations": [
      {
        "action": "Create index on users.email column",
        "impact": "High - Will reduce query time by ~95%",
        "risk": "Low - Non-blocking index creation available",
        "estimated_improvement": "250ms → 12ms"
      },
      {
        "action": "Review and optimize order_history query",
        "impact": "Medium - Missing index on created_at",
        "risk": "Low",
        "estimated_improvement": "180ms → 25ms"
      }
    ]
  }
}
```

#### **Step 3: Knowledge Base Search**

**Find Similar Issues & Solutions**
```python
from reasonops_sdk import ReasonOpsClient

client = ReasonOpsClient(base_url="http://localhost:8000")

# Search knowledge base for similar issues
kb_results = client.run_agents(
    agent_type="knowledge_base",
    context={
        "query": "database performance slow queries missing index",
        "category": "performance_optimization",
        "limit": 5
    }
)

print("📚 Knowledge Base Results:")
for i, result in enumerate(kb_results['articles'], 1):
    print(f"\n{i}. {result['title']}")
    print(f"   Relevance: {result['relevance_score']:.0%}")
    print(f"   Summary: {result['summary']}")
    print(f"   Link: {result['url']}")
```

**Knowledge Base Output:**
```
📚 Knowledge Base Results:

1. Database Index Strategy for High-Traffic Tables
   Relevance: 94%
   Summary: Best practices for creating indexes on frequently queried columns
   Link: /kb/articles/db-index-strategy

2. Non-Blocking Index Creation in PostgreSQL
   Relevance: 87%
   Summary: How to create indexes without locking production tables
   Link: /kb/articles/postgres-concurrent-index

3. Query Performance Troubleshooting Checklist
   Relevance: 82%
   Summary: Step-by-step guide to identify and fix slow queries
   Link: /kb/articles/query-performance-troubleshooting
```

#### **Step 4: Create Change Request for Index**

**Standard Change (Pre-approved)**
```python
# Create change for index creation
change = client.create_change({
    "title": "Create database index on users.email column",
    "description": "Create concurrent index to improve user_search query performance",
    "change_type": "standard",  # Pre-approved for index creation
    "category": "database_optimization",
    "risk_level": "low",
    "implementation_plan": [
        "CREATE INDEX CONCURRENTLY idx_users_email ON users(email)",
        "Verify index is used with EXPLAIN ANALYZE",
        "Monitor query performance for 15 minutes",
        "Update documentation"
    ],
    "rollback_plan": "DROP INDEX CONCURRENTLY idx_users_email",
    "testing_plan": "Run user_search query before/after, compare execution time",
    "estimated_duration": "30 minutes",
    "scheduled_date": datetime.now().isoformat(),
    "impact": "None - concurrent index creation, no table locking",
    "related_incident": "INC-2025-002"
})

print(f"✅ Change {change['id']} created and auto-approved (standard change)")
```

#### **Step 5: Implement Change**

**Execute Database Optimization**
```bash
# Using CLI to execute change
python cli.py changes:execute CHG-2025-157 --auto-approve

# Or via direct database command (tracked in change record)
psql -h prod-db-01 -U app_user -d production << EOF
-- Create index without locking table
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Verify index
\d users

-- Test query performance
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'test@example.com';
EOF
```

**Monitor Impact in Real-Time**
```python
# Use SDK to monitor change impact
import time

print("🔄 Implementing change...")
client.start_change_implementation(change['id'])

# Monitor for 15 minutes
for minute in range(15):
    time.sleep(60)
    
    metrics = client.get_performance_metrics({
        "metric": "database_query_time",
        "query": "user_search",
        "time_range": "last_1_minute"
    })
    
    print(f"Minute {minute + 1}: Avg response time = {metrics['avg_response_time']}ms")
    
    if metrics['avg_response_time'] < 20:
        print("✅ Performance target achieved!")
        break

client.complete_change_implementation(change['id'], {
    "status": "successful",
    "verification": "Query response time reduced from 250ms to 12ms"
})
```

**Output:**
```
🔄 Implementing change...
Minute 1: Avg response time = 245ms (index building)
Minute 2: Avg response time = 238ms
Minute 3: Avg response time = 15ms
Minute 4: Avg response time = 13ms
Minute 5: Avg response time = 12ms
✅ Performance target achieved!
```

#### **Step 6: Resolve Incident with Verification**

**Complete Resolution**
```python
# Resolve incident with detailed metrics
resolution = client.resolve_incident("INC-2025-002", {
    "resolution": "Created index on users.email column using concurrent build",
    "root_cause": "Missing database index on frequently queried column",
    "resolution_time": datetime.now().isoformat(),
    "metrics_before": {
        "avg_response_time": "250ms",
        "95th_percentile": "450ms",
        "queries_per_second": 4.2
    },
    "metrics_after": {
        "avg_response_time": "12ms",
        "95th_percentile": "18ms",
        "queries_per_second": 4.2
    },
    "improvement": "95% reduction in query time",
    "verification_steps": [
        "EXPLAIN ANALYZE confirms index usage",
        "15-minute monitoring shows stable performance",
        "No degradation in other queries",
        "No table locking during implementation"
    ]
})

print(f"✅ Incident {resolution['incident_id']} resolved")
print(f"   Performance improvement: {resolution['improvement']}")
```

#### **Step 7: Proactive Optimization**

**Schedule Additional Optimizations**
```python
# AI suggests additional optimizations
optimization_suggestions = client.run_agents(
    agent_type="proactive_optimization",
    context={
        "component": "database",
        "recent_incident": "INC-2025-002",
        "analyze_similar_risks": True
    }
)

print("\n🔮 Proactive Optimization Suggestions:")
for i, suggestion in enumerate(optimization_suggestions['suggestions'], 1):
    print(f"\n{i}. {suggestion['title']}")
    print(f"   Impact: {suggestion['estimated_impact']}")
    print(f"   Effort: {suggestion['estimated_effort']}")
    print(f"   Risk: {suggestion['risk_level']}")
    
    # Create change for each suggestion
    if suggestion['priority'] == 'high':
        change = client.create_change({
            "title": suggestion['title'],
            "description": suggestion['description'],
            "change_type": "standard",
            "scheduled_date": suggestion['recommended_date']
        })
        print(f"   📝 Change created: {change['id']}")
```

**AI Suggestions Output:**
```
🔮 Proactive Optimization Suggestions:

1. Add index on orders.created_at for order_history query
   Impact: 70% reduction in query time
   Effort: 30 minutes
   Risk: Low
   📝 Change created: CHG-2025-158

2. Implement query result caching for product_catalog
   Impact: 50% reduction in database load
   Effort: 4 hours
   Risk: Low
   📝 Change created: CHG-2025-159

3. Archive orders older than 2 years
   Impact: 40% reduction in table size
   Effort: 1 day
   Risk: Medium
```

### 📊 **Results Dashboard**

**Web UI: View Complete Incident Timeline**

Navigate to http://localhost:5173/incidents/INC-2025-002

```
┌─────────────────────────────────────────────────────────┐
│ Incident INC-2025-002: Database Performance Degradation │
├─────────────────────────────────────────────────────────┤
│ Status: ✅ Resolved                                      │
│ Priority: High                                          │
│ Duration: 47 minutes                                    │
│ SLA Status: ✅ Met (under 1 hour for high priority)    │
├─────────────────────────────────────────────────────────┤
│ Timeline:                                               │
│ 14:15 - Incident detected (automated monitoring)       │
│ 14:18 - AI analysis completed (3 min)                  │
│ 14:22 - Change request approved (4 min)                │
│ 14:25 - Index creation started (3 min)                 │
│ 14:40 - Performance verified (15 min)                  │
│ 15:02 - Incident resolved (22 min)                     │
├─────────────────────────────────────────────────────────┤
│ Performance Metrics:                                    │
│ Before: 250ms avg, 450ms p95                           │
│ After:  12ms avg, 18ms p95                             │
│ Improvement: 95% ⬆️                                     │
├─────────────────────────────────────────────────────────┤
│ Actions Taken:                                          │
│ ✅ Created index on users.email                         │
│ ✅ Verified performance improvement                     │
│ ✅ Scheduled 2 additional optimizations                 │
└─────────────────────────────────────────────────────────┘
```

### 🎯 **Key Takeaways**

1. **AI Detection:** Identified root cause (missing index) with 89% confidence
2. **Quick Resolution:** 47-minute end-to-end resolution
3. **Zero Downtime:** Concurrent index creation, no service interruption
4. **Proactive:** AI suggested 2 additional optimizations to prevent future issues
5. **Knowledge Reuse:** KB articles provided best practices

---

## Scenario 3: Automated Security Incident Response

### 📊 **Situation**
**Time:** 11:23 PM  
**Alert:** Unusual login pattern detected - 500 failed login attempts from single IP  
**Impact:** Potential brute force attack  
**Priority:** High (Security)

### 🔄 **Complete Workflow**

#### **Step 1: Security Alert Detection**

**Automated Security Monitoring**
```python
from reasonops_sdk import ReasonOpsClient
from datetime import datetime, timedelta

client = ReasonOpsClient(base_url="http://localhost:8000")

# Security monitoring system detects anomaly
security_event = {
    "event_type": "brute_force_attempt",
    "source_ip": "203.0.113.45",
    "failed_attempts": 500,
    "time_window": "5 minutes",
    "targeted_accounts": ["admin", "root", "administrator", "user1", "test"],
    "detected_at": datetime.now().isoformat(),
    "geo_location": "Unknown (VPN/Proxy detected)",
    "threat_score": 85  # High threat
}

# Auto-create security incident
incident = client.create_incident({
    "title": f"Security: Brute Force Attack from {security_event['source_ip']}",
    "description": f"{security_event['failed_attempts']} failed login attempts in {security_event['time_window']}",
    "priority": "high",
    "category": "security",
    "security_event": security_event,
    "auto_response_enabled": True
})

print(f"🚨 Security Incident: {incident['id']}")
```

#### **Step 2: AI Security Analysis**

**Automated Threat Assessment**
```python
# AI analyzes threat level and recommends immediate actions
threat_analysis = client.run_agents(
    agent_type="security_threat_analysis",
    context={
        "incident_id": incident['id'],
        "event_type": "brute_force",
        "source_ip": security_event['source_ip'],
        "failed_attempts": security_event['failed_attempts'],
        "targeted_accounts": security_event['targeted_accounts'],
        "threat_score": security_event['threat_score']
    }
)

print("\n🛡️ Threat Analysis:")
print(f"Threat Level: {threat_analysis['threat_level']}")
print(f"Attack Type: {threat_analysis['attack_type']}")
print(f"Confidence: {threat_analysis['confidence']:.0%}")
print(f"\nImmediate Actions Required:")
for action in threat_analysis['immediate_actions']:
    print(f"  🔴 {action['action']} (Priority: {action['priority']})")
```

**AI Output:**
```
🛡️ Threat Analysis:
Threat Level: HIGH
Attack Type: Automated brute force attack (likely botnet)
Confidence: 91%

Immediate Actions Required:
  🔴 Block source IP at firewall level (Priority: CRITICAL)
  🔴 Enable MFA for targeted accounts (Priority: HIGH)
  🔴 Review authentication logs for compromised accounts (Priority: HIGH)
  🔴 Notify security team (Priority: MEDIUM)
```

#### **Step 3: Automated Response (Auto-Remediation)**

**Execute Security Playbook**
```python
# Auto-remediation based on AI recommendations
remediation_result = client.execute_security_playbook({
    "incident_id": incident['id'],
    "playbook": "brute_force_response",
    "actions": [
        {
            "action": "block_ip",
            "target": security_event['source_ip'],
            "duration": "24_hours",
            "scope": "all_services"
        },
        {
            "action": "enable_mfa_enforcement",
            "target_accounts": security_event['targeted_accounts']
        },
        {
            "action": "force_password_reset",
            "target_accounts": ["admin", "root"],  # High-value accounts
            "reason": "security_precaution"
        },
        {
            "action": "notify_security_team",
            "urgency": "high",
            "include_details": True
        }
    ],
    "auto_execute": True  # Execute without manual approval for critical security
})

print("\n🤖 Automated Response Executed:")
for action_result in remediation_result['actions']:
    status = "✅" if action_result['success'] else "❌"
    print(f"{status} {action_result['action']}: {action_result['result']}")
```

**Output:**
```
🤖 Automated Response Executed:
✅ block_ip: IP 203.0.113.45 blocked at firewall for 24 hours
✅ enable_mfa_enforcement: MFA required for 5 accounts
✅ force_password_reset: Password reset emails sent to admin, root
✅ notify_security_team: Alert sent to security@company.com and Slack #security-alerts
```

#### **Step 4: Continuous Monitoring**

**Monitor for Continued Attack**
```python
import time

print("\n👁️ Monitoring for continued attack patterns...")

for minute in range(10):
    time.sleep(60)
    
    # Check for attack continuation
    attack_status = client.check_security_threat({
        "incident_id": incident['id'],
        "source_ip": security_event['source_ip'],
        "check_type": "continued_attack"
    })
    
    print(f"Minute {minute + 1}:")
    print(f"  - Failed attempts: {attack_status['failed_attempts_count']}")
    print(f"  - Status: {attack_status['status']}")
    
    if attack_status['status'] == 'mitigated':
        print("✅ Attack successfully mitigated!")
        break
    elif attack_status['new_source_ips']:
        print(f"⚠️ Attack shifted to new IPs: {', '.join(attack_status['new_source_ips'])}")
        # Trigger additional blocking
        for new_ip in attack_status['new_source_ips']:
            client.block_ip(new_ip, duration="24_hours")
```

**Output:**
```
👁️ Monitoring for continued attack patterns...
Minute 1:
  - Failed attempts: 2 (from IP blocked, returning firewall reject)
  - Status: blocking_effective
Minute 2:
  - Failed attempts: 0
  - Status: mitigated
✅ Attack successfully mitigated!
```

#### **Step 5: Forensic Analysis**

**Post-Incident Investigation**
```python
# Generate detailed forensic report
forensics = client.run_agents(
    agent_type="security_forensics",
    context={
        "incident_id": incident['id'],
        "analyze_period": "24_hours_before_attack",
        "include_logs": True,
        "check_data_breach": True
    }
)

print("\n🔍 Forensic Analysis:")
print(f"Data Breach Detected: {forensics['data_breach_detected']}")
print(f"Compromised Accounts: {len(forensics['compromised_accounts'])}")
print(f"\nAttack Pattern:")
print(f"  - First attempt: {forensics['attack_timeline']['first_attempt']}")
print(f"  - Peak rate: {forensics['attack_timeline']['peak_rate']} attempts/second")
print(f"  - Total attempts: {forensics['attack_timeline']['total_attempts']}")
print(f"  - Success rate: {forensics['attack_timeline']['success_rate']}")

if forensics['compromised_accounts']:
    print(f"\n⚠️ COMPROMISED ACCOUNTS:")
    for account in forensics['compromised_accounts']:
        print(f"  - {account['username']}: {account['compromise_type']}")
else:
    print(f"\n✅ No accounts compromised")
```

**Forensics Output:**
```
🔍 Forensic Analysis:
Data Breach Detected: False
Compromised Accounts: 0

Attack Pattern:
  - First attempt: 2025-10-22T23:18:32Z
  - Peak rate: 1.67 attempts/second
  - Total attempts: 500
  - Success rate: 0%

✅ No accounts compromised
```

#### **Step 6: Security Hardening**

**Implement Long-term Improvements**
```python
# Create change requests for security improvements
security_improvements = [
    {
        "title": "Implement rate limiting on authentication endpoints",
        "description": "Limit login attempts to 5 per IP per minute",
        "priority": "high",
        "estimated_effort": "4 hours"
    },
    {
        "title": "Deploy WAF rules for brute force protection",
        "description": "Configure Web Application Firewall with brute force detection",
        "priority": "high",
        "estimated_effort": "2 days"
    },
    {
        "title": "Enable automated IP reputation checking",
        "description": "Integrate with threat intelligence feeds to block known malicious IPs",
        "priority": "medium",
        "estimated_effort": "3 days"
    }
]

for improvement in security_improvements:
    change = client.create_change({
        **improvement,
        "change_type": "standard",
        "category": "security_enhancement",
        "related_incident": incident['id']
    })
    print(f"📝 Change created: {change['id']} - {improvement['title']}")
```

#### **Step 7: Incident Resolution & Reporting**

**Complete Security Incident**
```python
# Resolve with comprehensive details
resolution = client.resolve_incident(incident['id'], {
    "resolution": "Automated response blocked attacker IP, no accounts compromised",
    "root_cause": "Automated brute force attack from known botnet",
    "resolution_time": datetime.now().isoformat(),
    "security_impact": "None - attack mitigated before any successful logins",
    "actions_taken": [
        "Blocked source IP at firewall",
        "Enabled MFA for targeted accounts",
        "Forced password reset for admin accounts",
        "Notified security team",
        "Conducted forensic analysis"
    ],
    "follow_up_actions": [
        "CHG-2025-160: Implement rate limiting",
        "CHG-2025-161: Deploy WAF rules",
        "CHG-2025-162: Enable IP reputation checking"
    ],
    "compliance_notification": True,  # Notify compliance team
    "incident_report_generated": True
})

# Generate executive summary
exec_summary = client.generate_security_incident_summary(incident['id'])

print("\n" + "="*60)
print("🔒 SECURITY INCIDENT SUMMARY")
print("="*60)
print(exec_summary['markdown_report'])
```

**Executive Summary:**
```markdown
============================================================
🔒 SECURITY INCIDENT SUMMARY
============================================================

**Incident:** INC-2025-003
**Type:** Brute Force Attack
**Severity:** HIGH
**Status:** ✅ Resolved

**Timeline:**
- 23:23 - Attack detected (500 failed logins in 5 minutes)
- 23:24 - AI analysis completed (1 minute)
- 23:25 - Automated response executed (1 minute)
- 23:27 - Attack mitigated (2 minutes)
- 23:35 - Forensics completed (8 minutes)
- 23:40 - Incident resolved (15 minutes total)

**Impact:**
- ✅ No accounts compromised
- ✅ No data breach
- ✅ No service disruption
- ⚠️ 5 accounts required password reset (precautionary)

**Response Actions:**
1. Blocked attacker IP (203.0.113.45)
2. Enabled MFA for 5 targeted accounts
3. Reset passwords for admin accounts
4. Notified security team
5. Conducted forensic analysis

**Prevention Measures:**
- CHG-2025-160: Rate limiting (scheduled)
- CHG-2025-161: WAF deployment (scheduled)
- CHG-2025-162: IP reputation checking (scheduled)

**AI Contribution:**
- Detection to mitigation: 2 minutes
- Automated response: 100% successful
- False positives: 0

**Compliance:**
- Incident logged for audit
- Security team notified
- No breach notification required (no data compromised)

============================================================
```

### 🎯 **Key Takeaways**

1. **Speed:** 2-minute response time from detection to mitigation
2. **Automation:** 100% automated response, no manual intervention
3. **Effectiveness:** Zero compromised accounts, attack fully mitigated
4. **Prevention:** 3 security enhancements scheduled
5. **Compliance:** Complete audit trail and executive summary

---

## Scenario 4: Planned Infrastructure Migration

### 📊 **Situation**
**Project:** Migrate application from on-premise to Azure Kubernetes Service  
**Timeline:** 4-week migration window  
**Impact:** 20 microservices, 15 databases, 50 dependencies  
**Risk:** High

### 🔄 **Complete Workflow**

*[Continued in next section...]*

### 🎯 **Summary of All Scenarios**

| Scenario | Type | Duration | AI Impact | Automation % |
|----------|------|----------|-----------|--------------|
| 1. Production Outage | Incident | 12 min | 92% accuracy | 80% |
| 2. DB Performance | Problem | 47 min | 89% accuracy | 70% |
| 3. Security Attack | Security | 15 min | 91% accuracy | 100% |
| 4. Infrastructure Migration | Change | 4 weeks | Planning | 60% |
| 5. Service Desk Automation | Request | 2 min | 95% accuracy | 90% |
| 6. Capacity Planning | Proactive | Ongoing | Predictive | 85% |

---

## 🚀 Try These Scenarios Yourself!

All scenarios are available in the `examples/scenarios/` directory:

```bash
# Run scenario 1
python examples/scenarios/scenario1_production_outage.py

# Run scenario 2
python examples/scenarios/scenario2_database_performance.py

# Run scenario 3
python examples/scenarios/scenario3_security_incident.py
```

Each scenario includes:
- ✅ Complete working code
- ✅ Sample data
- ✅ Expected outputs
- ✅ Variations to try

---

**Ready to build your own scenarios?** Check out the [QUICKSTART.md](QUICKSTART.md) guide!
