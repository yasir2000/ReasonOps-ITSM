#!/usr/bin/env python3
"""
Scenario 1: Critical Production Outage
Complete end-to-end workflow demonstrating incident response with AI agents.

This scenario simulates:
- Production web app returning 503 errors
- AI-powered incident analysis
- Root cause identification
- Automated rollback
- Service restoration verification
- Post-incident documentation
"""

import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from reasonops_sdk import ReasonOpsClient


def print_banner(text: str):
    """Print formatted banner."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_step(step_num: int, title: str):
    """Print step header."""
    print(f"\n{'─' * 70}")
    print(f"STEP {step_num}: {title}")
    print(f"{'─' * 70}\n")


def simulate_delay(seconds: int, message: str = "Processing"):
    """Simulate processing with progress indicator."""
    print(f"{message}...", end="", flush=True)
    for _ in range(seconds):
        time.sleep(1)
        print(".", end="", flush=True)
    print(" ✓")


def main():
    """Run complete production outage scenario."""
    print_banner("SCENARIO 1: Critical Production Outage")
    print("🚨 Simulating production incident response with AI agents")
    print("⏱️  Estimated runtime: 30 seconds\n")
    
    # Initialize client
    print("Connecting to ReasonOps API...")
    client = ReasonOpsClient(base_url="http://localhost:8000")
    print("✅ Connected\n")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 1: Incident Detection & Creation
    # ─────────────────────────────────────────────────────────────────
    print_step(1, "Incident Detection & Creation")
    
    incident_data = {
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
    }
    
    print("📊 Monitoring Alert Received:")
    print(f"   - Service: web-app-prod")
    print(f"   - Error Rate: 98.5%")
    print(f"   - Status: All backends down")
    print(f"   - Impact: 5,000 users affected")
    
    simulate_delay(2, "Creating incident")
    
    # Simulate incident creation (would use real API)
    incident_id = "INC-2025-001"
    print(f"\n✅ Incident Created: {incident_id}")
    print(f"   Priority: CRITICAL")
    print(f"   Assigned: SRE On-Call Team")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 2: AI-Powered Incident Analysis
    # ─────────────────────────────────────────────────────────────────
    print_step(2, "AI-Powered Incident Analysis")
    
    analysis_context = {
        "incident_id": incident_id,
        "description": incident_data['description'],
        "priority": incident_data['priority'],
        "monitoring_data": incident_data['monitoring_data'],
        "recent_changes": True
    }
    
    print("🤖 Running AI Incident Analysis Agent...")
    print("   Analyzing monitoring data...")
    print("   Checking recent deployments...")
    print("   Reviewing infrastructure changes...")
    
    simulate_delay(3, "   AI processing")
    
    # Simulated AI analysis results
    print("\n📋 AI Analysis Results:")
    print("   Status: success")
    print("   Confidence: 92%")
    print("\n   Recommendations:")
    print("   1. Recent deployment detected 15 minutes ago (v2.1.0)")
    print("   2. Check application server logs for startup errors")
    print("   3. Verify database connection pool status")
    print("   4. Review load balancer health checks")
    print("   5. ⭐ Consider immediate rollback to v2.0.9 (last stable)")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 3: Root Cause Analysis
    # ─────────────────────────────────────────────────────────────────
    print_step(3, "Root Cause Analysis")
    
    print("🔍 Running RCA Agent...")
    print("   Analyzing deployment v2.1.0...")
    print("   Comparing with v2.0.9 configuration...")
    print("   Checking environment variables...")
    
    simulate_delay(2, "   Deep analysis")
    
    print("\n🎯 Root Cause Identified:")
    print("   Primary Cause: Configuration error in v2.1.0 deployment")
    print("   Contributing Factor: Missing DATABASE_URL environment variable")
    print("\n   Evidence:")
    print("   - All 6 app servers failing health checks")
    print("   - Application logs: 'DATABASE_URL environment variable not set'")
    print("   - Deployment manifest missing env var definition")
    print("   - v2.0.9 had correct configuration")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 4: Immediate Resolution (Rollback)
    # ─────────────────────────────────────────────────────────────────
    print_step(4, "Immediate Resolution - Rollback")
    
    print("🔄 Executing Emergency Rollback...")
    print("   Authorization: Emergency SRE approval")
    print("   Target Version: v2.0.9")
    print("   Method: Blue-Green deployment switch")
    
    simulate_delay(3, "   Rolling back")
    
    print("\n✅ Rollback Completed:")
    print("   - All traffic routed to v2.0.9 backends")
    print("   - v2.1.0 containers terminated")
    print("   - Load balancer updated")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 5: Service Restoration Verification
    # ─────────────────────────────────────────────────────────────────
    print_step(5, "Service Restoration Verification")
    
    print("✓ Health Check: Monitoring recovery...")
    
    # Simulate progressive recovery
    recovery_steps = [
        ("Backend health checks", "6/6 healthy"),
        ("Error rate", "0.2%"),
        ("Response time", "145ms"),
        ("Load balancer", "All backends operational")
    ]
    
    for metric, value in recovery_steps:
        simulate_delay(1, f"   Checking {metric}")
        print(f" → {value}")
    
    print("\n✅ SERVICE FULLY RESTORED")
    print("   - All metrics within normal range")
    print("   - User traffic resumed")
    print("   - No data loss")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 6: Incident Resolution & Documentation
    # ─────────────────────────────────────────────────────────────────
    print_step(6, "Incident Resolution & Documentation")
    
    resolution_time = datetime.now()
    downtime_minutes = 12
    
    print("📝 Completing Incident Documentation...")
    
    print(f"\n✅ Incident {incident_id} RESOLVED")
    print(f"   Resolution Time: {resolution_time.strftime('%H:%M:%S')}")
    print(f"   Total Downtime: {downtime_minutes} minutes")
    print(f"   SLA Status: ✅ MET (under 15-minute target)")
    print(f"\n   Resolution: Rolled back deployment v2.1.0 to v2.0.9")
    print(f"   Root Cause: Missing DATABASE_URL environment variable")
    print(f"\n   Preventive Actions:")
    print(f"   - Add DATABASE_URL validation to CI/CD pipeline")
    print(f"   - Implement pre-deployment configuration checks")
    print(f"   - Update deployment checklist")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 7: Create Problem Record
    # ─────────────────────────────────────────────────────────────────
    print_step(7, "Create Problem Record for Prevention")
    
    print("📋 Creating Problem Record...")
    
    simulate_delay(1, "   Generating problem analysis")
    
    problem_id = "PRB-2025-042"
    print(f"\n✅ Problem {problem_id} Created")
    print(f"   Title: Deployment process lacks configuration validation")
    print(f"   Related Incident: {incident_id}")
    print(f"   Proposed Solution: Implement pre-deployment config checker")
    print(f"   Estimated Effort: 2 days")
    
    # ─────────────────────────────────────────────────────────────────
    # FINAL SUMMARY
    # ─────────────────────────────────────────────────────────────────
    print_banner("INCIDENT SUMMARY REPORT")
    
    print(f"Incident ID: {incident_id}")
    print(f"Title: Production Web App - 503 Service Unavailable")
    print(f"Priority: CRITICAL")
    print(f"Status: ✅ RESOLVED")
    print(f"\nTimeline:")
    print(f"  03:47 - Incident detected (automated monitoring)")
    print(f"  03:50 - AI analysis completed (3 min)")
    print(f"  03:52 - Root cause identified (2 min)")
    print(f"  03:55 - Rollback initiated (3 min)")
    print(f"  03:59 - Service restored (4 min)")
    print(f"  Total Resolution Time: 12 minutes ✅")
    print(f"\nImpact:")
    print(f"  - Affected Users: 5,000")
    print(f"  - Service Downtime: 12 minutes")
    print(f"  - Data Loss: None")
    print(f"  - SLA Compliance: ✅ Met")
    print(f"\nAI Contribution:")
    print(f"  - Analysis Time: 3 seconds")
    print(f"  - Recommendation Accuracy: 92%")
    print(f"  - Time Saved: ~20 minutes (vs manual analysis)")
    print(f"\nFollow-up Actions:")
    print(f"  - Problem Record: {problem_id}")
    print(f"  - Change Request: CHG-2025-156 (scheduled)")
    print(f"  - Post-Mortem: Scheduled for tomorrow")
    
    print("\n" + "=" * 70)
    print("✅ SCENARIO COMPLETE")
    print("=" * 70)
    print("\n💡 Key Learnings:")
    print("   - AI identified root cause in seconds")
    print("   - Automated analysis enabled fast decision-making")
    print("   - Complete incident lifecycle demonstrated")
    print("   - SLA met with time to spare")
    print("\n🚀 Try modifying the scenario:")
    print("   - Change incident priority")
    print("   - Add more monitoring data")
    print("   - Test different resolution strategies")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Scenario interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error running scenario: {e}")
        sys.exit(1)
