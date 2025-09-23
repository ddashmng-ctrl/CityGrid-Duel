#!/usr/bin/env python3
"""
Sync the leaderboard section from README.md to docs/index.md
This script reads the leaderboard section from README.md and copies it to docs/index.md
while preserving the rest of the index.md content.
"""

import re
import os


def extract_leaderboard_section(readme_path):
    """Extract the leaderboard section from README.md"""
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the leaderboard section
    # Pattern: from "## 🏆 Leaderboard" to the next "## " (level 2 header) or "---" or end of file
    pattern = r'(## 🏆 Leaderboard.*?)(?=^## [^🏆]|^---|\Z)'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    
    if match:
        return match.group(1).strip()
    else:
        return None


def update_index_with_leaderboard(index_path, leaderboard_content):
    """Update docs/index.md with the leaderboard section while preserving other content"""
    # Read the current index.md
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if leaderboard section already exists
    leaderboard_pattern = r'## 🏆 Leaderboard.*?(?=^##|\Z)'
    
    if re.search(leaderboard_pattern, content, re.MULTILINE | re.DOTALL):
        # Replace existing leaderboard section
        new_content = re.sub(
            leaderboard_pattern, 
            leaderboard_content, 
            content, 
            flags=re.MULTILINE | re.DOTALL
        )
    else:
        # Add leaderboard section at the end
        new_content = content.rstrip() + '\n\n' + leaderboard_content + '\n'
    
    # Write the updated content
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(new_content)


def main():
    """Main function to sync leaderboard from README to index"""
    # Define paths relative to the repository root
    readme_path = 'README.md'
    index_path = 'docs/index.md'
    
    # Verify files exist
    if not os.path.exists(readme_path):
        print(f"Error: {readme_path} not found")
        return 1
    
    if not os.path.exists(index_path):
        print(f"Error: {index_path} not found")
        return 1
    
    # Extract leaderboard section
    leaderboard_content = extract_leaderboard_section(readme_path)
    
    if leaderboard_content is None:
        print("Error: Could not find leaderboard section in README.md")
        return 1
    
    print(f"Found leaderboard section ({len(leaderboard_content)} characters)")
    
    # Update index.md
    update_index_with_leaderboard(index_path, leaderboard_content)
    
    print(f"Successfully updated {index_path} with leaderboard content")
    return 0


if __name__ == '__main__':
    exit(main())