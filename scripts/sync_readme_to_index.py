#!/usr/bin/env python3
"""
Sync README.md content to docs/index.md to keep them synchronized.

This script ensures that the main README.md content is reflected in the
docs/index.md file for GitHub Pages, while preserving any docs-specific
content like links and dashboard information.
"""

import os
import sys
from pathlib import Path


def read_readme_content():
    """Read the README.md file content."""
    readme_path = Path("README.md")
    if not readme_path.exists():
        raise FileNotFoundError("README.md not found in the repository root")
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        return f.read()


def transform_readme_for_docs(readme_content):
    """Transform README content for the docs/index.md file."""
    # For now, we'll use the README content as-is, but we could add
    # transformations here if needed (e.g., adjusting relative links)
    
    # Add a header comment to indicate this is auto-generated
    header = "<!-- This file is auto-generated from README.md. Do not edit directly. -->\n\n"
    
    return header + readme_content


def write_index_content(content):
    """Write the transformed content to docs/index.md."""
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    index_path = docs_dir / "index.md"
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Successfully synchronized content to {index_path}")


def main():
    """Main function to sync README.md to docs/index.md."""
    try:
        # Change to repository root if script is run from scripts directory
        script_dir = Path(__file__).parent
        repo_root = script_dir.parent
        os.chdir(repo_root)
        
        print("🔄 Synchronizing README.md to docs/index.md...")
        
        # Read README content
        readme_content = read_readme_content()
        print(f"📖 Read {len(readme_content)} characters from README.md")
        
        # Transform content for docs
        index_content = transform_readme_for_docs(readme_content)
        
        # Write to docs/index.md
        write_index_content(index_content)
        
        print("✅ Synchronization complete!")
        
    except Exception as e:
        print(f"❌ Error during synchronization: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()