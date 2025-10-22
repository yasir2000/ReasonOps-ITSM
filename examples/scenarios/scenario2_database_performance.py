#!/usr/bin/env python3
"""
Scenario 2: Database Performance Degradation
End-to-end workflow for performance optimization with AI guidance.

This scenario simulates:
- Database query performance degradation
- AI-powered performance analysis
- Knowledge base search for solutions
- Change management for optimization
- Real-time performance monitoring
- Proactive optimization recommendations
"""

import sys
import time
from datetime import datetime
from pathlib import Path

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


def print_metrics(label: str, metrics: dict):
    """Print performance metrics."""
    print(f"\n📊 {label}:")
    for key, value in metrics.items():
        print(f"   - {key}: {value}")


def main():
    """Run database performance scenario."""
    print_banner("SCENARIO 2: Database Performance Degradation")
    print("🐢 Simulating database performance optimization with AI")
    print("⏱️  Estimated runtime: 45 seconds\n")
    
    # Initialize
    print("Connecting to ReasonOps API...")
    client = ReasonOpsClient(base_url="http://localhost:8000")
    print("✅ Connected\n")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 1: Performance Monitoring Detection
    # ─────────────────────────────────────────────────────────────────
    print_step(1, "Performance Monitoring Detection")
    
    print("📈 Performance Monitoring Alert:")
    print("   Service: PostgreSQL Database (prod-db-01)")
    print("   Alert: Query response time degradation")
    
    metrics_before = {
        "Baseline Response Time": "50ms",
        "Current Response Time": "250ms",
        "Degradation": "400% ⬆️",
        "Affected Queries": "user_search, order_history, product_catalog"
    }
    print_metrics("Current Metrics", metrics_before)
    
    simulate_delay(2, "Creating incident")
    
    incident_id = "INC-2025-002"
    print(f"\n✅ Incident Created: {incident_id}")
    print(f"   Priority: HIGH")
    print(f"   Category: Performance")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 2: AI Performance Analysis
    # ─────────────────────────────────────────────────────────────────
    print_step(2, "AI Performance Analysis")
    
    print("🤖 Running Performance Analysis Agent...")
    print("   Analyzing query execution plans...")
    print("   Checking database indexes...")
    print("   Reviewing table statistics...")
    
    simulate_delay(3, "   AI analyzing")
    
    print("\n🎯 AI Analysis Results:")
    print("   Status: success")
    print("   Confidence: 89%")
    print("\n   Primary Issue:")
    print("   ⚠️  Missing database index on users.email column")
    print("\n   Evidence:")
    print("   - EXPLAIN ANALYZE shows full table scan on users table")
    print("   - users table has 2.5M rows")
    print("   - user_search query runs 15,000 times/hour")
    print("   - No index on email column (used in WHERE clause)")
    print("\n   Recommendations:")
    print("   1. ⭐ Create index on users.email column")
    print("      Impact: High - Will reduce query time by ~95%")
    print("      Risk: Low - Non-blocking index creation available")
    print("      Estimated: 250ms → 12ms")
    print("   2. Review order_history query (missing index on created_at)")
    print("      Impact: Medium - 70% improvement possible")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 3: Knowledge Base Search
    # ─────────────────────────────────────────────────────────────────
    print_step(3, "Knowledge Base Search")
    
    print("📚 Searching knowledge base for similar issues...")
    
    simulate_delay(2, "   Searching")
    
    print("\n✅ Relevant Articles Found:")
    print("\n   1. Database Index Strategy for High-Traffic Tables")
    print("      Relevance: 94%")
    print("      Summary: Best practices for creating indexes on frequently")
    print("               queried columns")
    print("      Link: /kb/articles/db-index-strategy")
    print("\n   2. Non-Blocking Index Creation in PostgreSQL")
    print("      Relevance: 87%")
    print("      Summary: How to create indexes without locking production tables")
    print("      Link: /kb/articles/postgres-concurrent-index")
    print("\n   3. Query Performance Troubleshooting Checklist")
    print("      Relevance: 82%")
    print("      Link: /kb/articles/query-performance-troubleshooting")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 4: Create Change Request
    # ─────────────────────────────────────────────────────────────────
    print_step(4, "Create Change Request")
    
    print("📝 Creating Change Request...")
    print("   Type: Standard (pre-approved for index creation)")
    print("   Category: Database Optimization")
    print("   Risk: LOW")
    
    simulate_delay(1, "   Generating change plan")
    
    change_id = "CHG-2025-157"
    print(f"\n✅ Change {change_id} Created and Auto-Approved")
    print(f"   Title: Create database index on users.email column")
    print(f"\n   Implementation Plan:")
    print(f"   1. CREATE INDEX CONCURRENTLY idx_users_email ON users(email)")
    print(f"   2. Verify index is used with EXPLAIN ANALYZE")
    print(f"   3. Monitor query performance for 15 minutes")
    print(f"   4. Update documentation")
    print(f"\n   Rollback Plan:")
    print(f"   - DROP INDEX CONCURRENTLY idx_users_email")
    print(f"\n   Impact: None (concurrent creation, no table locking)")
    print(f"   Duration: ~30 minutes")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 5: Implement Change
    # ─────────────────────────────────────────────────────────────────
    print_step(5, "Implement Database Optimization")
    
    print("🔧 Executing Change...")
    print("   Running: CREATE INDEX CONCURRENTLY idx_users_email ON users(email)")
    
    simulate_delay(3, "   Creating index (concurrent, non-blocking)")
    
    print("\n✅ Index Created Successfully")
    print("   Index: idx_users_email")
    print("   Table: users")
    print("   Column: email")
    print("   Method: btree")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 6: Real-time Performance Monitoring
    # ─────────────────────────────────────────────────────────────────
    print_step(6, "Real-time Performance Monitoring")
    
    print("👁️  Monitoring query performance (simulated 15-minute window)...")
    
    # Simulate progressive improvement
    performance_data = [
        (1, 245, "Index building"),
        (2, 238, ""),
        (3, 15, "Index active"),
        (4, 13, ""),
        (5, 12, "Performance stable")
    ]
    
    for minute, response_time, status in performance_data:
        time.sleep(1)
        status_text = f" - {status}" if status else ""
        print(f"   Minute {minute}: Avg response time = {response_time}ms{status_text}")
        
        if response_time < 20:
            print("\n✅ Performance Target Achieved!")
            print(f"   - Response time reduced to {response_time}ms")
            print(f"   - 95% improvement from baseline")
            break
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 7: Verify and Document
    # ─────────────────────────────────────────────────────────────────
    print_step(7, "Verification & Resolution")
    
    print("✓ Running verification checks...")
    
    verification_checks = [
        "EXPLAIN ANALYZE confirms index usage",
        "95th percentile response time under 20ms",
        "No degradation in other queries",
        "No table locking during implementation"
    ]
    
    for check in verification_checks:
        simulate_delay(1, f"   {check}")
    
    print(f"\n✅ Incident {incident_id} RESOLVED")
    
    metrics_after = {
        "Avg Response Time": "12ms (was 250ms)",
        "95th Percentile": "18ms (was 450ms)",
        "Queries/Second": "4.2 (unchanged)",
        "Improvement": "95% reduction in query time ⬇️"
    }
    print_metrics("Final Metrics", metrics_after)
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 8: Proactive Optimization
    # ─────────────────────────────────────────────────────────────────
    print_step(8, "Proactive Optimization Suggestions")
    
    print("🔮 AI analyzing for additional optimization opportunities...")
    
    simulate_delay(2, "   Running proactive analysis")
    
    print("\n💡 Additional Optimizations Recommended:")
    print("\n   1. Add index on orders.created_at for order_history query")
    print("      Impact: 70% reduction in query time")
    print("      Effort: 30 minutes")
    print("      Risk: Low")
    print("      📝 Change CHG-2025-158 created")
    print("\n   2. Implement query result caching for product_catalog")
    print("      Impact: 50% reduction in database load")
    print("      Effort: 4 hours")
    print("      Risk: Low")
    print("      📝 Change CHG-2025-159 created")
    print("\n   3. Archive orders older than 2 years")
    print("      Impact: 40% reduction in table size")
    print("      Effort: 1 day")
    print("      Risk: Medium")
    
    # ─────────────────────────────────────────────────────────────────
    # FINAL SUMMARY
    # ─────────────────────────────────────────────────────────────────
    print_banner("PERFORMANCE OPTIMIZATION REPORT")
    
    print(f"Incident ID: {incident_id}")
    print(f"Title: Database Performance Degradation - Slow Queries")
    print(f"Status: ✅ RESOLVED")
    print(f"\nTimeline:")
    print(f"  14:15 - Performance degradation detected")
    print(f"  14:18 - AI analysis completed (3 min)")
    print(f"  14:22 - Change request approved (4 min)")
    print(f"  14:25 - Index creation started (3 min)")
    print(f"  14:40 - Performance verified (15 min)")
    print(f"  15:02 - Incident resolved (47 min total)")
    print(f"\nPerformance Impact:")
    print(f"  Before: 250ms avg, 450ms p95")
    print(f"  After:  12ms avg, 18ms p95")
    print(f"  Improvement: 95% ⬆️")
    print(f"\nChange Management:")
    print(f"  - Primary Change: {change_id} (completed)")
    print(f"  - Follow-up Changes: 2 scheduled")
    print(f"  - Zero Downtime: ✅ Concurrent index creation")
    print(f"\nAI Contribution:")
    print(f"  - Root cause identified: 89% confidence")
    print(f"  - Knowledge base articles: 3 relevant")
    print(f"  - Proactive suggestions: 3 additional optimizations")
    print(f"  - Time saved: ~2 hours (vs manual analysis)")
    print(f"\nKnowledge Captured:")
    print(f"  - Index creation documented")
    print(f"  - Performance baseline updated")
    print(f"  - Best practices applied")
    
    print("\n" + "=" * 70)
    print("✅ SCENARIO COMPLETE")
    print("=" * 70)
    print("\n💡 Key Learnings:")
    print("   - AI identified missing index as root cause")
    print("   - Knowledge base provided implementation guidance")
    print("   - Zero-downtime optimization achieved")
    print("   - Proactive suggestions prevent future issues")
    print("\n🚀 Try modifying the scenario:")
    print("   - Change the degradation percentage")
    print("   - Add more affected queries")
    print("   - Test different database types")
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
