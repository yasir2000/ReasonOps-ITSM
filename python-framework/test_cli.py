#!/usr/bin/env python3
"""
ReasonOps ITSM CLI Test Suite

Comprehensive tests for the CLI functionality.
"""

import subprocess
import json
import sys
import os
from pathlib import Path

def run_cli_command(command: list, expect_success: bool = True) -> tuple:
    """Run a CLI command and return result"""
    try:
        result = subprocess.run(
            ["python", "-m", "cli"] + command,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        success = result.returncode == 0
        if expect_success and not success:
            print(f"❌ Command failed: {' '.join(command)}")
            print(f"   Return code: {result.returncode}")
            print(f"   STDERR: {result.stderr}")
            return False, result
        elif not expect_success and success:
            print(f"❌ Command should have failed: {' '.join(command)}")
            return False, result
        else:
            print(f"✅ Command succeeded: {' '.join(command)}")
            return True, result
            
    except Exception as e:
        print(f"❌ Exception running command {' '.join(command)}: {e}")
        return False, None

def test_basic_commands():
    """Test basic CLI commands"""
    print("\n🧪 Testing Basic Commands")
    
    tests = [
        # System commands
        (["system", "version"], True),
        (["system", "status"], True),
        (["system", "status", "--json"], True),
        
        # Dashboard
        (["dashboard"], True),
        (["dashboard", "--json"], True),
        
        # Help commands
        (["--help"], True),
        (["system", "--help"], True),
        (["practices", "--help"], True),
    ]
    
    passed = 0
    total = len(tests)
    
    for command, expect_success in tests:
        success, _ = run_cli_command(command, expect_success)
        if success:
            passed += 1
    
    print(f"\n📊 Basic Commands: {passed}/{total} passed")
    return passed == total

def test_practice_commands():
    """Test ITIL practice commands"""
    print("\n🧪 Testing ITIL Practice Commands")
    
    tests = [
        # Incident management
        (["practices", "incident", "list"], True),
        (["practices", "incident", "list", "--json"], True),
        (["practices", "incident", "list", "--limit", "5"], True),
        
        # Problem management
        (["practices", "problem", "list"], True),
        (["practices", "problem", "list", "--json"], True),
        
        # Change management
        (["practices", "change", "list"], True),
        (["practices", "change", "list", "--json"], True),
    ]
    
    passed = 0
    total = len(tests)
    
    for command, expect_success in tests:
        success, _ = run_cli_command(command, expect_success)
        if success:
            passed += 1
    
    print(f"\n📊 Practice Commands: {passed}/{total} passed")
    return passed == total

def test_cmdb_commands():
    """Test CMDB commands"""
    print("\n🧪 Testing CMDB Commands")
    
    tests = [
        # CMDB operations
        (["cmdb", "list"], True),
        (["cmdb", "list", "--json"], True),
        (["cmdb", "list", "--limit", "5"], True),
    ]
    
    passed = 0
    total = len(tests)
    
    for command, expect_success in tests:
        success, _ = run_cli_command(command, expect_success)
        if success:
            passed += 1
    
    print(f"\n📊 CMDB Commands: {passed}/{total} passed")
    return passed == total

def test_agent_commands():
    """Test AI agent commands"""
    print("\n🧪 Testing AI Agent Commands")
    
    tests = [
        # Agent management
        (["agents", "providers"], True),
        (["agents", "providers", "--json"], True),
        (["agents", "health"], True),
        (["agents", "health", "--json"], True),
        (["agents", "decisions"], True),
        (["agents", "decisions", "--json"], True),
        (["agents", "decisions", "--limit", "5"], True),
    ]
    
    passed = 0
    total = len(tests)
    
    for command, expect_success in tests:
        success, _ = run_cli_command(command, expect_success)
        if success:
            passed += 1
    
    print(f"\n📊 Agent Commands: {passed}/{total} passed")
    return passed == total

def test_data_commands():
    """Test data operation commands"""
    print("\n🧪 Testing Data Operation Commands")
    
    tests = [
        # Data operations
        (["data", "rollups", "--collection", "incidents"], True),
        (["data", "rollups", "--collection", "incidents", "--json"], True),
    ]
    
    passed = 0
    total = len(tests)
    
    for command, expect_success in tests:
        success, _ = run_cli_command(command, expect_success)
        if success:
            passed += 1
    
    print(f"\n📊 Data Commands: {passed}/{total} passed")
    return passed == total

def test_slm_commands():
    """Test SLM commands"""
    print("\n🧪 Testing SLM Commands")
    
    tests = [
        # SLM operations
        (["slm", "metrics"], True),
        (["slm", "metrics", "--json"], True),
        (["slm", "metrics", "--days", "7"], True),
    ]
    
    passed = 0
    total = len(tests)
    
    for command, expect_success in tests:
        success, _ = run_cli_command(command, expect_success)
        if success:
            passed += 1
    
    print(f"\n📊 SLM Commands: {passed}/{total} passed")
    return passed == total

def test_additional_commands():
    """Test additional utility commands"""
    print("\n🧪 Testing Additional Commands")
    
    tests = [
        # Metrics
        (["metrics", "show"], True),
        (["metrics", "show", "--json"], True),
        (["metrics", "show", "--type", "incidents"], True),
        
        # Jobs
        (["jobs", "list"], True),
        (["jobs", "list", "--json"], True),
        
        # Security
        (["security", "audit"], True),
        (["security", "audit", "--json"], True),
        (["security", "audit", "--type", "access"], True),
        
        # Configuration
        (["config", "show"], True),
        (["config", "show", "--json"], True),
        
        # Workflow
        (["workflow", "list"], True),
        (["workflow", "list", "--json"], True),
        
        # Catalog
        (["catalog", "list"], True),
        (["catalog", "list", "--json"], True),
        
        # Knowledge
        (["knowledge", "search", "test"], True),
        (["knowledge", "search", "test", "--json"], True),
        
        # Testing
        (["test", "validate"], True),
        (["test", "validate", "--json"], True),
    ]
    
    passed = 0
    total = len(tests)
    
    for command, expect_success in tests:
        success, _ = run_cli_command(command, expect_success)
        if success:
            passed += 1
    
    print(f"\n📊 Additional Commands: {passed}/{total} passed")
    return passed == total

def test_json_output():
    """Test JSON output parsing"""
    print("\n🧪 Testing JSON Output")
    
    json_commands = [
        ["system", "status", "--json"],
        ["dashboard", "--json"],
        ["practices", "incident", "list", "--json"],
        ["agents", "providers", "--json"],
        ["metrics", "show", "--json"],
    ]
    
    passed = 0
    total = len(json_commands)
    
    for command in json_commands:
        success, result = run_cli_command(command, True)
        if success and result:
            try:
                json.loads(result.stdout)
                print(f"✅ Valid JSON output for: {' '.join(command)}")
                passed += 1
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON output for: {' '.join(command)} - {e}")
        elif not success:
            print(f"❌ Command failed: {' '.join(command)}")
    
    print(f"\n📊 JSON Output: {passed}/{total} passed")
    return passed == total

def test_error_handling():
    """Test error handling"""
    print("\n🧪 Testing Error Handling")
    
    error_tests = [
        # Invalid commands
        (["invalid-command"], False),
        (["practices", "invalid-practice"], False),
        (["cmdb", "invalid-operation"], False),
        
        # Invalid arguments
        (["practices", "incident", "show", "INVALID_ID"], True),  # Should handle gracefully
        (["cmdb", "show", "INVALID_CI"], True),  # Should handle gracefully
    ]
    
    passed = 0
    total = len(error_tests)
    
    for command, expect_success in error_tests:
        success, _ = run_cli_command(command, expect_success)
        if success:
            passed += 1
    
    print(f"\n📊 Error Handling: {passed}/{total} passed")
    return passed == total

def main():
    """Run all CLI tests"""
    print("🚀 ReasonOps ITSM CLI Test Suite")
    print("=" * 50)
    
    test_results = []
    
    # Run all test suites
    test_results.append(test_basic_commands())
    test_results.append(test_practice_commands())
    test_results.append(test_cmdb_commands())
    test_results.append(test_agent_commands())
    test_results.append(test_data_commands())
    test_results.append(test_slm_commands())
    test_results.append(test_additional_commands())
    test_results.append(test_json_output())
    test_results.append(test_error_handling())
    
    # Summary
    passed_suites = sum(test_results)
    total_suites = len(test_results)
    
    print("\n" + "=" * 50)
    print("📋 Test Suite Summary")
    print("=" * 50)
    print(f"Total test suites: {total_suites}")
    print(f"Passed: {passed_suites}")
    print(f"Failed: {total_suites - passed_suites}")
    
    if passed_suites == total_suites:
        print("\n🎉 All tests passed! CLI is working correctly.")
        return 0
    else:
        print(f"\n❌ {total_suites - passed_suites} test suite(s) failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())