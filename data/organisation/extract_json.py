#!/usr/bin/env python3
"""Extract JSON from markdown file."""
import json
import re
import sys
from pathlib import Path

def extract_json_from_markdown(md_file: str, output_file: str = None):
    """Extract JSON from markdown code block."""
    md_path = Path(md_file)
    if not md_path.exists():
        print(f"❌ File not found: {md_file}", file=sys.stderr)
        sys.exit(1)
    
    content = md_path.read_text()
    
    # Extract JSON from markdown code block
    match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
    if not match:
        print(f"❌ Could not find JSON code block in {md_file}", file=sys.stderr)
        sys.exit(1)
    
    json_str = match.group(1)
    
    try:
        # Parse and validate JSON
        data = json.loads(json_str)
        
        # Determine output file
        if output_file is None:
            output_file = md_path.with_suffix('.json')
        else:
            output_file = Path(output_file)
        
        # Write JSON file
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Created {output_file}")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: extract_json.py <markdown_file> [output_file]")
        sys.exit(1)
    
    extract_json_from_markdown(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)

