#!/usr/bin/env python3
"""
Quick test of the optimized Azure DevOps pipeline triggering
Tests the performance improvements with authentication caching
"""

import time
from server import bb7_trigger_bulk, check_azure_cli_auth, clear_auth_cache

def test_performance():
    print("🚀 Testing Optimized Azure DevOps Pipeline Performance")
    print("=" * 60)
    
    # Test 1: Clear cache and time first auth check
    print("\n⏱️  Test 1: First authentication check (no cache)")
    clear_auth_cache()
    start_time = time.time()
    auth_result = check_azure_cli_status()
    first_auth_time = time.time() - start_time
    print(f"First auth check took: {first_auth_time:.2f} seconds")
    print(f"Auth status: {'✅ Success' if auth_result.get('authenticated') else '❌ Failed'}")
    
    # Test 2: Time second auth check (should use cache)
    print("\n⏱️  Test 2: Second authentication check (cached)")
    start_time = time.time()
    auth_result2 = check_azure_cli_status()
    second_auth_time = time.time() - start_time
    print(f"Cached auth check took: {second_auth_time:.2f} seconds")
    print(f"Speed improvement: {((first_auth_time - second_auth_time) / first_auth_time * 100):.1f}% faster")
    
    # Test 3: Trigger integration pipeline 2 times with timing
    if auth_result.get("authenticated"):
        print("\n🚀 Test 3: Triggering integration pipeline 2 times")
        start_time = time.time()
        
        try:
            results = bb7_trigger_bulk("integration", 2)
            total_time = time.time() - start_time
            
            print(f"Pipeline trigger completed in: {total_time:.2f} seconds")
            print(f"Average time per run: {total_time/2:.2f} seconds")
            
            # Show results
            for i, result in enumerate(results, 1):
                if result.get("success"):
                    print(f"✅ Run {i}: Success - Run ID {result.get('run_id')}")
                else:
                    print(f"❌ Run {i}: Failed - {result.get('error')}")
        
        except Exception as e:
            print(f"❌ Pipeline trigger failed: {e}")
    else:
        print("\n❌ Skipping pipeline test - authentication failed")
    
    print(f"\n📊 Performance Summary:")
    print(f"   • First auth check: {first_auth_time:.2f}s")
    print(f"   • Cached auth check: {second_auth_time:.2f}s")
    print(f"   • Cache speed improvement: {((first_auth_time - second_auth_time) / first_auth_time * 100):.1f}%")
    print(f"\n🎯 Optimizations implemented:")
    print(f"   ✅ Authentication caching (5 min)")
    print(f"   ✅ Reduced CLI timeouts (30s vs 60s)")
    print(f"   ✅ Optimized Azure CLI path discovery")
    print(f"   ✅ Faster primary path detection")

if __name__ == "__main__":
    test_performance()
