#!/usr/bin/env python3
"""
Verify that docs/index.md contains the latest leaderboard table from README.md.
This script ensures the leaderboard section is synchronized before GitHub Pages deployment.
"""

import re
import sys
import os


def extract_leaderboard_section(content):
    """Extract the leaderboard section from markdown content."""
    # Look for the leaderboard section starting with "## 🏆 Leaderboard"
    pattern = r'## 🏆 Leaderboard\s*\n(.*?)(?=\n## |\n---|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    return None


def normalize_content(content):
    """Normalize content for comparison by removing extra whitespace."""
    if content is None:
        return ""
    # Remove extra whitespace and normalize line endings
    return re.sub(r'\s+', ' ', content.strip())


def main():
    """Main verification function."""
    readme_path = "README.md"
    docs_path = "docs/index.md"
    
    # Check if files exist
    if not os.path.exists(readme_path):
        print(f"ERROR: {readme_path} not found")
        sys.exit(1)
    
    if not os.path.exists(docs_path):
        print(f"ERROR: {docs_path} not found")
        sys.exit(1)
    
    # Read files
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()
    
    with open(docs_path, 'r', encoding='utf-8') as f:
        docs_content = f.read()
    
    # Extract leaderboard sections
    readme_leaderboard = extract_leaderboard_section(readme_content)
    docs_leaderboard = extract_leaderboard_section(docs_content)
    
    # Normalize for comparison
    readme_normalized = normalize_content(readme_leaderboard)
    docs_normalized = normalize_content(docs_leaderboard)
    
    print("=== Leaderboard Verification ===")
    print(f"README.md leaderboard: {'Found' if readme_leaderboard else 'Not found'}")
    print(f"docs/index.md leaderboard: {'Found' if docs_leaderboard else 'Not found'}")
    
    if readme_leaderboard is None:
        print("WARNING: No leaderboard section found in README.md")
        # If README has no leaderboard, docs shouldn't either
        if docs_leaderboard is None:
            print("✅ PASS: Both files have no leaderboard section")
            sys.exit(0)
        else:
            print("❌ FAIL: docs/index.md has leaderboard but README.md doesn't")
            sys.exit(1)
    
    if docs_leaderboard is None:
        print("❌ FAIL: README.md has leaderboard but docs/index.md is missing it")
        print("\nExpected leaderboard content from README.md:")
        print("=" * 50)
        print(readme_leaderboard)
        print("=" * 50)
        sys.exit(1)
    
    # Compare normalized content
    if readme_normalized == docs_normalized:
        print("✅ PASS: Leaderboard sections match")
        sys.exit(0)
    else:
        print("❌ FAIL: Leaderboard sections do not match")
        print("\nREADME.md leaderboard:")
        print("=" * 50)
        print(readme_leaderboard)
        print("=" * 50)
        print("\ndocs/index.md leaderboard:")
        print("=" * 50)
        print(docs_leaderboard)
        print("=" * 50)
        sys.exit(1)


if __name__ == "__main__":
    main()