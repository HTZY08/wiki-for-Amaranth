#!/usr/bin/env python3
"""
Fix frontmatter in all .md files under the wiki docs.
Ensures each file has valid YAML frontmatter bounded by --- lines,
with a title field present.
"""
import sys
import yaml
from pathlib import Path

DOCS_DIR = Path("/opt/data/projects/wiki/src/content/docs/hermes/官方文档")


def get_title_from_filename(filepath):
    """Generate a reasonable title from the filename."""
    stem = filepath.stem
    # Remove common prefixes
    for prefix in [
        "apple-", "autonomous-ai-agents-", "blockchain-", "creative-",
        "data-science-", "devops-", "dogfood-", "email-", "finance-",
        "gaming-", "github-", "health-", "mcp-", "media-", "migration-",
        "mlops-", "note-taking-", "payments-", "productivity-",
        "research-", "security-", "smart-home-", "social-media-",
        "software-development-", "web-development-", "yuanbao-",
    ]:
        if stem.startswith(prefix):
            stem = stem[len(prefix):]
            break
    # Replace hyphens/underscores with spaces, title case
    name = stem.replace('-', ' ').replace('_', ' ').strip()
    return name.title() if name else stem


def fix_file(filepath):
    """Fix frontmatter for a single .md file. Returns True if changed."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    lines = content.split('\n')

    # --- Step 1: Normalize the opening --- line ---
    # If the file starts with `---` but not `---\n`, the first line has
    # content mixed with `---`. Extract it.
    mixed_content = None
    if not content.startswith('---\n') and content.startswith('---'):
        first = lines[0]
        # Remove the leading `---`
        rest = first[3:].strip()
        # If rest ends with `---` (e.g. "--- frontmatter ---"), strip it
        if rest.endswith('---'):
            rest = rest[:-3].strip()
        if rest:
            mixed_content = rest
        # Replace first line with just `---`
        lines[0] = '---'
        content = '\n'.join(lines)
        lines = content.split('\n')

    # --- Step 2: Find the frontmatter bounds ---
    # Must start with ---
    if not content.startswith('---\n'):
        # No frontmatter at all
        title = get_title_from_filename(filepath)
        new_fm = f'---\ntitle: "{title}"\n---\n\n'
        content = new_fm + content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  NO frontmatter → added default title '{title}' for {filepath.name}")
        return True

    # Find closing ---
    close_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            close_idx = i
            break

    if close_idx is None:
        # No closing ---
        # Everything from line 1 onward is frontmatter — this is broken
        title = get_title_from_filename(filepath)
        new_fm = f'---\ntitle: "{title}"\n---\n\n'
        # Keep content after the first --- as body (it might be content)
        body = '\n'.join(lines[1:]).strip()
        content = new_fm + body
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  UNCLOSED frontmatter → rewrote for {filepath.name}")
        return True

    # We have opening and closing --- markers
    fm_lines = lines[1:close_idx]
    body = '\n'.join(lines[close_idx + 1:])

    # If we had mixed content from step 1, prepend it
    if mixed_content is not None:
        fm_lines.insert(0, mixed_content)

    fm_text = '\n'.join(fm_lines).strip()

    # --- Step 3: Parse and validate YAML ---
    # Try to parse
    try:
        data = yaml.safe_load(fm_text)
    except yaml.YAMLError:
        data = None

    needs_rewrite = False
    title = None

    if data is None:
        # Frontmatter is empty or unparseable
        data = {}
        needs_rewrite = True
    elif not isinstance(data, dict):
        # Frontmatter is a scalar / list, not a dict
        data = {}
        needs_rewrite = True

    # Check for title
    if not data.get('title'):
        title = get_title_from_filename(filepath)
        data['title'] = title
        needs_rewrite = True

    if not needs_rewrite:
        return False  # No changes needed

    # Rewrite frontmatter preserving existing fields
    new_fm = yaml.dump(data, allow_unicode=True, default_flow_style=False).strip()
    content = f'---\n{new_fm}\n---\n\n{body.lstrip(chr(10))}'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    reason = []
    if mixed_content:
        reason.append(f"mixed-line")
    if 'title' in data and title:
        reason.append(f"added title '{title}'")
    if data == {} and not title:
        reason.append("empty->default")
    print(f"  Fixed [{', '.join(reason)}] {filepath.name}")
    return True


def main():
    md_files = sorted(DOCS_DIR.rglob('*.md'))
    print(f"Found {len(md_files)} .md files")

    fixed = 0
    errors = 0

    for fp in md_files:
        try:
            if fix_file(fp):
                fixed += 1
        except Exception as e:
            errors += 1
            print(f"  ❌ Error: {fp.name}: {e}", file=sys.stderr)

    print(f"\nDone: {fixed} files fixed, {errors} errors")


if __name__ == '__main__':
    main()
