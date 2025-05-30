#!/usr/bin/env python3
"""
Test script for the CLI-based MCP server.
This script tests all the main functionality without running the full MCP server.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our server functions
from server import (
    check_azure_cli_status,
    list_available_pipelines,
    test_pipeline_access,
    bb7_list_runs,
    load_config,
    pipelines
)

def test_azure_cli_status():
    """Test Azure CLI status check."""
    print("🔍 Testing Azure CLI status...")
    status = check_azure_cli_status()
    print(f"✅ Azure CLI Status: {status}")
    return status["authenticated"] if "authenticated" in status else False

def test_list_pipelines():
    """Test listing available pipelines."""
    print("\n📋 Testing pipeline listing...")
    result = list_available_pipelines()
    print(f"✅ Found {result['total_pipelines']} pipelines")
    for pipeline in result['pipelines'][:3]:  # Show first 3
        print(f"  - {pipeline['name']} (ID: {pipeline['pipeline_id']})")
    return result['total_pipelines'] > 0

def test_pipeline_access_functionality():
    """Test pipeline access for the first configured pipeline."""
    print("\n🔐 Testing pipeline access...")
    if not pipelines:
        print("❌ No pipelines configured")
        return False
    
    # Test the first pipeline
    first_pipeline = list(pipelines.keys())[0]
    print(f"Testing access to: {first_pipeline}")
    
    result = test_pipeline_access(first_pipeline)
    if result.get("success"):
        print(f"✅ {result['access_test']}")
        print(f"  Pipeline Name: {result['pipeline_info']['name']}")
        print(f"  Pipeline Type: {result['pipeline_info']['type']}")
        return True
    else:
        print(f"❌ {result.get('access_test', 'Failed')}")
        print(f"  Error: {result.get('error', 'Unknown error')}")
        return False

def test_list_runs():
    """Test listing pipeline runs."""
    print("\n📊 Testing pipeline runs listing...")
    if not pipelines:
        print("❌ No pipelines configured")
        return False
    
    # Test the first pipeline
    first_pipeline = list(pipelines.keys())[0]
    print(f"Getting recent runs for: {first_pipeline}")
    
    result = bb7_list_runs(first_pipeline, 3)
    if result.get("success"):
        print(f"✅ Found {result['count']} recent runs")
        return True
    else:
        print(f"❌ Failed to get runs: {result.get('error', 'Unknown error')}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing AdoMcp CLI-based MCP Server")
    print("=" * 50)
    
    # Test results
    results = []
    
    # Test 1: Azure CLI Status
    results.append(("Azure CLI Status", test_azure_cli_status()))
    
    # Test 2: List Pipelines
    results.append(("List Pipelines", test_list_pipelines()))
    
    # Test 3: Pipeline Access (only if CLI is working)
    if results[0][1]:  # If Azure CLI is working
        results.append(("Pipeline Access", test_pipeline_access_functionality()))
        results.append(("List Runs", test_list_runs()))
    else:
        print("\n⚠️  Skipping pipeline tests due to Azure CLI issues")
    
    # Summary
    print("\n" + "=" * 50)
    print("📈 Test Results Summary:")
    
    passed = 0
    for test_name, passed_test in results:
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if passed_test:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! The CLI-based MCP server is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
