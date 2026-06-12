#!/usr/bin/env python3
"""
Remove L3/L4/L5 labels and --- separators from section files.
Run after Phase 9 (depth expansion) before Phase 10 (quality round).

Safe: only matches exact L3/L4/L5 patterns, leaves normal ## headings untouched.
"""
import re, os, glob

SECTIONS = "/opt/data/reviews/<project>/sections"

for fpath in sorted(glob.glob(os.path.join(SECTIONS, "*.md"))):
    if os.path.basename(fpath).startswith("00-"):
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content
    
    # Remove heading markers like "## L3 量化层：..." or "### L3 ..."
    content = re.sub(r'^#{2,3}\s+L[345]\s+[^\n]*\n', '', content, flags=re.MULTILINE)
    # Remove horizontal rules
    content = re.sub(r'^\s*---+\s*$', '', content, flags=re.MULTILINE)
    # Remove bold L3/L4/L5 labels: "**L3：..." or "**L3:..."
    content = re.sub(r'\*\*L[345][：:]\s*', '', content)
    content = re.sub(r'\*\*L[345]\s+', '', content)
    # Clean up excess blank lines
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    if content != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Cleaned: {os.path.basename(fpath)}")
print("Done. Remember to rebuild PDF.")
