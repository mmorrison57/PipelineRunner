#!/usr/bin/env python3
"""
Script to trigger integration pipeline 2 times with websites repo current branch
"""

from server import bb7_trigger_bulk, find_repository_by_name, get_current_branch_from_repo

def main():
    print("🚀 Triggering integration pipeline with websites repo current branch...")
    
    try:
        # Step 1: Find the websites repository
        repo = find_repository_by_name("websites")
        if not repo:
            print("❌ Repository 'websites' not found")
            return
        
        print(f"✅ Found repository: {repo['name']}")
        print(f"   Path: {repo['path']}")
        
        # Step 2: Get current branch from the repository
        branch = get_current_branch_from_repo(repo['path'])
        if not branch:
            print("❌ Could not get current branch from repository")
            return
        
        print(f"✅ Current branch: {branch}")
        
        # Step 3: Trigger the integration pipeline 2 times
        print(f"\n🔄 Triggering integration pipeline 2 times with branch '{branch}'...")
        
        result = bb7_trigger_bulk("integration", 2, repo="websites")
        
        print("✅ Pipeline trigger completed!")
        print(f"📊 Result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
