#!/usr/bin/env python3
"""
Sync leaderboard content from README.md to docs/index.md
This script extracts the verified results and leaderboard sections from README.md
and updates the docs/index.md file for GitHub Pages.
"""

import re
import os
from pathlib import Path

def extract_leaderboard_sections(readme_content):
    """Extract the verified results and leaderboard sections from README.md"""
    
    # Extract the "Verified Results" section - more flexible pattern
    verified_pattern = r'(## ✅ Verified Results.*?)(?=\n## [^#]|\nFor collaborations|\n---|\Z)'
    verified_match = re.search(verified_pattern, readme_content, re.DOTALL)
    verified_section = verified_match.group(1).strip() if verified_match else ""
    
    # Extract the "Leaderboard" section - more flexible pattern  
    leaderboard_pattern = r'(## 🏆 Leaderboard.*?)(?=\n---|\n## [^#]|\Z)'
    leaderboard_match = re.search(leaderboard_pattern, readme_content, re.DOTALL)
    leaderboard_section = leaderboard_match.group(1).strip() if leaderboard_match else ""
    
    return verified_section, leaderboard_section

def update_index_md(verified_section, leaderboard_section, index_path):
    """Update the docs/index.md file with the extracted content"""
    
    # Read current index.md content
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        # Create basic structure if file doesn't exist
        content = """# CityGrid-Duel Dashboard

World's first auditable AI duel platform.

## Links

- [Logs Directory](../logs/)
- [Soul Debate Documentation](../docs/soul_debate/README.md)

## Latest Results Snapshot

*Coming Soon!*
"""
    
    # Prepare the leaderboard content
    leaderboard_content = f"""## Latest Results

{verified_section}

{leaderboard_section}

---

*This leaderboard is automatically synchronized from README.md*
*Last updated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}*"""
    
    # Split content into lines for easier processing
    lines = content.split('\n')
    new_lines = []
    skip_until_next_section = False
    found_latest_results = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Handle "Latest Results Snapshot" placeholder
        if line.strip() == "## Latest Results Snapshot":
            new_lines.append(leaderboard_content)
            # Skip the following lines until the next section or empty line + "*Coming Soon!*"
            i += 1
            while i < len(lines) and not lines[i].startswith('## '):
                i += 1
            i -= 1  # Back up one to let the main loop handle the next section
            found_latest_results = True
            
        # Handle existing "Latest Results" section
        elif line.strip() == "## Latest Results":
            if not found_latest_results:
                new_lines.append(leaderboard_content)
                found_latest_results = True
            # Skip everything until we find the next section that's not "Latest Results"
            skip_until_next_section = True
                
        # Stop skipping when we hit a different section (not starting with our timestamp pattern)
        elif skip_until_next_section and (line.startswith('## ') and 
                                          not line.strip().startswith("## ✅") and 
                                          not line.strip().startswith("## 🏆") and
                                          line.strip() != "## Latest Results"):
            skip_until_next_section = False
            new_lines.append(line)
            
        # Skip timestamp lines and sync messages from previous runs
        elif line.strip().startswith("*This leaderboard is automatically synchronized") or \
             line.strip().startswith("*Last updated:"):
            # Skip these lines
            pass
            
        # Normal line processing
        elif not skip_until_next_section:
            new_lines.append(line)
            
        i += 1
    
    # If we never found a latest results section, add it after Links
    if not found_latest_results:
        final_lines = []
        links_end = -1
        
        # Find the end of the Links section
        for i, line in enumerate(new_lines):
            if line.startswith('## Links'):
                # Find where this section ends
                j = i + 1
                while j < len(new_lines) and not new_lines[j].startswith('## '):
                    j += 1
                links_end = j
                break
        
        if links_end > -1:
            # Insert after Links section
            final_lines = new_lines[:links_end] + ['', leaderboard_content, ''] + new_lines[links_end:]
        else:
            # Just append at the end
            final_lines = new_lines + ['', leaderboard_content]
        
        new_lines = final_lines
    
    return '\n'.join(new_lines)

def main():
    """Main function to sync leaderboard content"""
    
    # Define paths
    repo_root = Path(__file__).parent.parent
    readme_path = repo_root / "README.md"
    index_path = repo_root / "docs" / "index.md"
    
    # Ensure docs directory exists
    index_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Read README.md
    if not readme_path.exists():
        print(f"Error: {readme_path} not found")
        return 1
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()
    
    # Extract leaderboard sections
    verified_section, leaderboard_section = extract_leaderboard_sections(readme_content)
    
    if not verified_section and not leaderboard_section:
        print("Warning: No leaderboard sections found in README.md")
        return 1
    
    # Update index.md
    updated_content = update_index_md(verified_section, leaderboard_section, index_path)
    
    # Write updated content
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"Successfully updated {index_path}")
    print(f"Extracted verified results: {bool(verified_section)}")
    print(f"Extracted leaderboard: {bool(leaderboard_section)}")
    
    return 0

if __name__ == "__main__":
    exit(main())