#!/usr/bin/env python3
"""
Test repository detection and pipeline triggering with repository context.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import (
    list_repositories, 
    find_repository, 
    get_repository_branch,
    trigger_pipeline_with_repo
)

def test_repository_functions():
    """Test all repository-related functions."""
    
    print("🧪 Testing Repository Management Functions")
    print("=" * 60)
    
    # Test 1: List repositories
    print("\n📋 Test 1: List all repositories")
    repos = list_repositories()
    if repos.get("total_repositories", 0) > 0:
        print(f"✅ Found {repos['total_repositories']} repositories:")
        for repo in repos['repositories'][:3]:  # Show first 3
            print(f"  - {repo['name']}: {repo['description']}")
            print(f"    Path: {repo['path']}")
            print(f"    Aliases: {', '.join(repo['aliases'])}")
    else:
        print(f"❌ No repositories found: {repos}")
        return False
    
    # Test 2: Find repository by exact name
    print(f"\n🔍 Test 2: Find repository by exact name 'Antares-Websites'")
    result = find_repository("Antares-Websites")
    if result.get("success"):
        repo = result["repository"]
        print(f"✅ Found: {repo['name']}")
        print(f"   Path: {repo['path']}")
        print(f"   Aliases: {', '.join(repo['aliases'])}")
    else:
        print(f"❌ Not found: {result}")
    
    # Test 3: Find repository by alias
    print(f"\n🔍 Test 3: Find repository by alias 'websites'")
    result = find_repository("websites")
    if result.get("success"):
        repo = result["repository"]
        print(f"✅ Found: {repo['name']} (matched alias)")
    else:
        print(f"❌ Not found: {result}")
    
    # Test 4: Find repository by partial name
    print(f"\n🔍 Test 4: Find repository by partial name 'antares'")
    result = find_repository("antares")
    if result.get("success"):
        repo = result["repository"]
        print(f"✅ Found: {repo['name']} (partial match)")
    else:
        print(f"❌ Not found: {result}")
    
    # Test 5: Get current branch from Antares-Websites
    print(f"\n🌿 Test 5: Get current branch from 'websites' repository")
    result = get_repository_branch("websites")
    if result.get("success"):
        print(f"✅ Current branch: {result['current_branch']}")
        print(f"   Repository: {result['repository']}")
        print(f"   Path: {result['path']}")
    else:
        print(f"❌ Failed: {result}")
    
    # Test 6: Trigger pipeline with repository (dry run - just test the detection)
    print(f"\n🚀 Test 6: Test pipeline trigger with repository (detection only)")
    # We'll just test the repository detection part, not actually trigger
    repo = find_repository("websites")
    if repo.get("success"):
        branch_result = get_repository_branch("websites")
        if branch_result.get("success"):
            print(f"✅ Would trigger integration pipeline with:")
            print(f"   Repository: {branch_result['repository']}")
            print(f"   Branch: {branch_result['current_branch']}")
            print(f"   Path: {branch_result['path']}")
        else:
            print(f"❌ Could not get branch: {branch_result}")
    else:
        print(f"❌ Repository not found: {repo}")
    
    print(f"\n🎯 Repository management tests complete!")
    return True

if __name__ == "__main__":
    success = test_repository_functions()
    sys.exit(0 if success else 1)
