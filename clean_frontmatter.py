#!/usr/bin/env python3
"""Clean up `|--- frontmatter ---` garbage lines and fix missing titles."""

import os
import re
import yaml

DOCS_DIR = "/opt/data/projects/wiki/src/content/docs/hermes/官方文档"


def infer_title_from_content(lines):
    """Try to infer a title from the first heading in the file content."""
    for line in lines:
        m = re.match(r'^#\s+(.+?)\s*$', line.strip())
        if m:
            return m.group(1).strip()
    return None


def write_file_safe(filepath, lines):
    """Write lines to file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def clean_file(filepath):
    """Remove '|--- frontmatter ---' line and fix missing titles."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.splitlines(keepends=True)
    if not lines:
        return False
    
    modified = False
    
    # Check for '--- frontmatter ---' garbage on line 1
    if '--- frontmatter ---' in lines[0]:
        print(f"  Removing '--- frontmatter ---' from line 1")
        lines.pop(0)
        modified = True
    
    # Now check: does the file have a proper frontmatter?
    if not lines or lines[0].strip() != '---':
        # No frontmatter — add one
        title = infer_title_from_content(lines)
        if not title:
            basename = os.path.splitext(os.path.basename(filepath))[0]
            title = basename.replace('-', ' ').replace('_', ' ').title()
        print(f"  Adding frontmatter with title: {title}")
        new_lines = ['---\n', f'title: {title}\n', '---\n']
        # If the first lines were empty or --- body ---, skip them
        new_lines.extend(lines)
        lines = new_lines
        modified = True
        write_file_safe(filepath, lines)
        return modified
    
    # Find the closing ---
    dash_indices = [i for i, l in enumerate(lines) if l.strip() == '---']
    if len(dash_indices) < 2:
        # Start was found but no closing — add one
        title = infer_title_from_content(lines[dash_indices[0]+1:])
        if not title:
            basename = os.path.splitext(os.path.basename(filepath))[0]
            title = basename.replace('-', ' ').replace('_', ' ').title()
        print(f"  Incomplete frontmatter — replacing with title: {title}")
        new_lines = ['---\n', f'title: {title}\n', '---\n']
        new_lines.extend(lines[dash_indices[0]+1:])
        lines = new_lines
        modified = True
        write_file_safe(filepath, lines)
        return modified
    
    fm_end = dash_indices[1]
    fm_content = ''.join(lines[1:fm_end]).strip()
    
    if not fm_content:
        # Empty frontmatter — add a title
        title = infer_title_from_content(lines[fm_end+1:])
        if not title:
            basename = os.path.splitext(os.path.basename(filepath))[0]
            title = basename.replace('-', ' ').replace('_', ' ').title()
        print(f"  Empty frontmatter — adding title: {title}")
        new_lines = ['---\n', f'title: {title}\n', '---\n']
        new_lines.extend(lines[fm_end + 1:])
        lines = new_lines
        modified = True
    else:
        # Parse YAML and check for title
        try:
            fields = yaml.safe_load(fm_content)
            if isinstance(fields, dict) and ('title' not in fields or not fields['title']):
                title = infer_title_from_content(lines[fm_end+1:])
                if not title:
                    basename = os.path.splitext(os.path.basename(filepath))[0]
                    title = basename.replace('-', ' ').replace('_', ' ').title()
                print(f"  Missing title in frontmatter — adding: {title}")
                fields['title'] = title
                new_yaml = yaml.dump(fields, allow_unicode=True, default_flow_style=False, sort_keys=False, width=4096).strip()
                new_lines = ['---\n', new_yaml, '\n---\n']
                new_lines.extend(lines[fm_end + 1:])
                lines = new_lines
                modified = True
        except yaml.YAMLError:
            # Content between --- is not valid YAML — rebuild frontmatter
            title = infer_title_from_content(lines[fm_end+1:])
            if not title:
                basename = os.path.splitext(os.path.basename(filepath))[0]
                title = basename.replace('-', ' ').replace('_', ' ').title()
            print(f"  Invalid YAML frontmatter — replacing with title: {title}")
            new_lines = ['---\n', f'title: {title}\n', '---\n']
            new_lines.extend(lines[fm_end + 1:])
            lines = new_lines
            modified = True
    
    if modified:
        write_file_safe(filepath, lines)
    
    return modified


def main():
    fixed_count = 0
    
    for root, dirs, files in os.walk(DOCS_DIR):
        for fname in sorted(files):
            if not fname.endswith('.md'):
                continue
            filepath = os.path.join(root, fname)
            rel = os.path.relpath(filepath, DOCS_DIR)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                first_line = f.readline()
            
            if '--- frontmatter ---' in first_line:
                if clean_file(filepath):
                    fixed_count += 1
                    print(f"  -> Fixed: {rel}")
    
    print(f"\nCleaned {fixed_count} files.")
    return fixed_count


if __name__ == '__main__':
    main()
