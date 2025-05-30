#!/usr/bin/env python3
"""
Quick test of MCP tools to see their return structure
"""

from server import find_repository, get_repository_branch, list_repositories
import json

print('Testing MCP tools directly:')
print('1. list_repositories():')
result1 = list_repositories()
print(json.dumps(result1, indent=2))
print(f"Type: {type(result1)}")

print('\n2. find_repository("websites"):')
result2 = find_repository('websites')
print(json.dumps(result2, indent=2))
print(f"Type: {type(result2)}")

print('\n3. get_repository_branch("websites"):')
result3 = get_repository_branch('websites')
print(json.dumps(result3, indent=2))
print(f"Type: {type(result3)}")
