#!/usr/bin/env python3
"""
Test the enhanced bb7_trigger_bulk function with branch override - single test.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import bb7_trigger_bulk

def test_branch_override_single():
    """Test the branch override functionality with a single call."""
    
    print("🧪 Testing bb7_trigger_bulk with 'dev' branch override")
    print("=" * 50)
    
    # Test: Override with dev branch
    print(f"\n📋 Triggering integration pipeline 1 time with 'dev' branch")
    result = bb7_trigger_bulk("integration", 1, "dev")
    
    if result and len(result) > 0:
        first_result = result[0]
        if first_result.get("success"):
            print(f"✅ Pipeline triggered successfully!")
            print(f"   Pipeline: {first_result.get('pipeline_name')}")
            print(f"   Branch Used: {first_result.get('branch_used')}")
            print(f"   Run ID: {first_result.get('run_id')}")
            print(f"   URL: {first_result.get('url')}")
            
            web_url = first_result.get('web_url')
            if web_url:
                print(f"   Web URL: {web_url}")
        else:
            print(f"❌ Pipeline trigger failed:")
            print(f"   Error: {first_result.get('error')}")
    else:
        print(f"❌ No results returned: {result}")
    
    print(f"\n🎯 Test complete!")

if __name__ == "__main__":
    test_branch_override_single()
