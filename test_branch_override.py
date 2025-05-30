#!/usr/bin/env python3
"""
Test the enhanced bb7_trigger_bulk function with branch override.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import bb7_trigger_bulk

def test_branch_override():
    """Test the branch override functionality."""
    
    print("🧪 Testing bb7_trigger_bulk with branch override")
    print("=" * 50)
    
    # Test 1: Use default branch from config
    print("\n📋 Test 1: Using default branch from config")
    result1 = bb7_trigger_bulk("integration", 1)
    if result1 and len(result1) > 0 and result1[0].get("success"):
        print(f"✅ Success! Used branch: {result1[0].get('branch_used', 'unknown')}")
        print(f"   Run ID: {result1[0].get('run_id')}")
    else:
        print(f"❌ Failed: {result1}")
    
    # Test 2: Override with dev branch
    print(f"\n📋 Test 2: Override with 'dev' branch")
    result2 = bb7_trigger_bulk("integration", 1, "dev")
    if result2 and len(result2) > 0 and result2[0].get("success"):
        print(f"✅ Success! Used branch: {result2[0].get('branch_used', 'unknown')}")
        print(f"   Run ID: {result2[0].get('run_id')}")
    else:
        print(f"❌ Failed: {result2}")
    
    print(f"\n🎯 Branch override functionality test complete!")

if __name__ == "__main__":
    test_branch_override()
